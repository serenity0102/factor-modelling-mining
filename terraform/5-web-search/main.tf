provider "aws" {
  region  = "us-east-1"
  profile = "factor" # your aws profile
}

# Variables
variable "tickers" {
  description = "List of stock ticker symbols (e.g. DJIA 30)"
  type        = list(string)
  default     = ["AAPL", "AMGN", "AMZN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX", "DIS", "GS", "HD", "HON", "IBM", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "NVDA", "PG", "SHW", "TRV", "UNH", "V", "VZ", "WMT"]
}

variable "s3_bucket_prefix" {
  description = "Prefix for S3 bucket name"
  type        = string
  default     = "stock-news-data"
}

variable "tavily_api_key" {
  description = "API key for Tavily web search service"
  type        = string
  sensitive   = true
  # This will be provided via environment variable TF_VAR_tavily_api_key
}

# Random string for S3 bucket name uniqueness
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  lower   = true
  upper   = false
}

# Local for S3 bucket name
locals {
  s3_bucket_name = "${var.s3_bucket_prefix}-${random_string.bucket_suffix.result}"
}

# S3 bucket for storing news data
resource "aws_s3_bucket" "news_bucket" {
  bucket = local.s3_bucket_name
}

resource "aws_s3_bucket_ownership_controls" "news_bucket" {
  bucket = aws_s3_bucket.news_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "news_bucket" {
  depends_on = [aws_s3_bucket_ownership_controls.news_bucket]
  bucket     = aws_s3_bucket.news_bucket.id
  acl        = "private"
}

# Store Tavily API key in Secrets Manager
resource "aws_secretsmanager_secret" "tavily_api_key" {
  name        = "TAVILY_API_KEY_${random_string.bucket_suffix.result}"
  description = "API Key for Tavily web search service"
}

resource "aws_secretsmanager_secret_version" "tavily_api_key" {
  secret_id     = aws_secretsmanager_secret.tavily_api_key.id
  secret_string = var.tavily_api_key != "" ? var.tavily_api_key : "dummy-api-key-for-testing"
}

# IAM role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "stock_news_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policy for Lambda to write to S3, access Secrets Manager, and CloudWatch Logs
resource "aws_iam_policy" "lambda_policy" {
  name        = "stock_news_lambda_policy"
  description = "Policy for stock news Lambda function"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Effect   = "Allow"
        Resource = [
          aws_s3_bucket.news_bucket.arn,
          "${aws_s3_bucket.news_bucket.arn}/*"
        ]
      },
      {
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Effect   = "Allow"
        Resource = [
          aws_secretsmanager_secret.tavily_api_key.arn
        ]
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# Create Lambda deployment package
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../src/web-search"
  output_path = "${path.module}/lambda_function.zip"
}

# Lambda function
resource "aws_lambda_function" "stock_news_lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "stock_news_fetcher"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.9"
  timeout          = 60
  memory_size      = 256

  environment {
    variables = {
      S3_BUCKET          = aws_s3_bucket.news_bucket.id
      TAVILY_API_KEY_NAME = aws_secretsmanager_secret.tavily_api_key.name
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_policy_attachment
  ]
}

# EventBridge rule to trigger Lambda daily
resource "aws_cloudwatch_event_rule" "daily_trigger" {
  name                = "daily-stock-news-trigger"
  description         = "Triggers stock news Lambda function daily"
  schedule_expression = "cron(0 0 * * ? *)" # Run at midnight UTC every day
}

# Single EventBridge target that passes ticker as input
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.daily_trigger.name
  target_id = "stock_news_lambda"
  arn       = aws_lambda_function.stock_news_lambda.arn
  
  input = jsonencode({
    tickers = var.tickers
    date    = "$${aws:CurrentDate}"  # This will be resolved at runtime to the current date
  })
}

# Permission for EventBridge to invoke Lambda
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.stock_news_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_trigger.arn
}

# Outputs
output "s3_bucket_name" {
  value = aws_s3_bucket.news_bucket.id
}

output "lambda_function_name" {
  value = aws_lambda_function.stock_news_lambda.function_name
}

output "eventbridge_rule_name" {
  value = aws_cloudwatch_event_rule.daily_trigger.name
}
