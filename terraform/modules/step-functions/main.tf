# IAM Role for Step Functions
resource "aws_iam_role" "step_function_role" {
  name = "${var.project_name}-step-function-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Step Functions to invoke Batch jobs
resource "aws_iam_policy" "step_function_policy" {
  name = "${var.project_name}-step-function-policy"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "batch:SubmitJob",
          "batch:DescribeJobs",
          "batch:TerminateJob"
        ]
        Effect = "Allow"
        Resource = "*"
      },
      {
        Action = [
          "events:PutTargets",
          "events:PutRule",
          "events:DescribeRule"
        ]
        Effect = "Allow"
        Resource = "*"
      },
      {
        Action = [
          "lambda:InvokeFunction"
        ]
        Effect = "Allow"
        Resource = "*"
      }
    ]
  })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "step_function_policy_attachment" {
  role       = aws_iam_role.step_function_role.name
  policy_arn = aws_iam_policy.step_function_policy.arn
}

# Lambda function to calculate date ranges
resource "aws_lambda_function" "calculate_date_ranges" {
  function_name = "${var.project_name}-calculate-date-ranges"
  handler       = "lambda_function.lambda_handler"
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.9"
  filename      = "${path.module}/lambda/calculate_date_ranges.zip"
  
  environment {
    variables = {
      DEFAULT_N = "5"  # Default number of date ranges
    }
  }
}

# Lambda function to calculate ticker groups
resource "aws_lambda_function" "calculate_ticker_groups" {
  function_name = "${var.project_name}-calculate-ticker-groups"
  handler       = "lambda_function.lambda_handler"
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.9"
  filename      = "${path.module}/lambda/calculate_ticker_groups.zip"
  
  environment {
    variables = {
      DEFAULT_M = "6"  # Default number of ticker groups
    }
  }
}

# IAM Role for Lambda functions
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

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

# Attach basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# AWS Batch Job Definition
resource "aws_batch_job_definition" "factor_mining_job" {
  name = "${var.project_name}-job-definition"
  type = "container"
  
  container_properties = jsonencode({
    image = var.ecr_repository_url,
    vcpus = var.batch_vcpus,
    memory = var.batch_memory,
    command = ["python", "run_factor_analysis.py", "--tickers", "Ref::DJIA_TICKERS", "--start-date", "Ref::START_DATE", "--end-date", "Ref::END_DATE", "--batch-no", "Ref::BATCH_NO"],
    jobRoleArn = aws_iam_role.batch_job_role.arn,
    environment = [
      {
        name = "CLICKHOUSE_HOST",
        value = var.clickhouse_endpoint
      },
      {
        name = "CLICKHOUSE_PORT",
        value = tostring(var.clickhouse_port)
      }
    ]
  })
}

# IAM Role for Batch Jobs
resource "aws_iam_role" "batch_job_role" {
  name = "${var.project_name}-batch-job-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Attach policies to Batch Job Role as needed
resource "aws_iam_role_policy_attachment" "batch_job_policy" {
  role       = aws_iam_role.batch_job_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

# AWS Batch Compute Environment
resource "aws_batch_compute_environment" "factor_mining_compute" {
  compute_environment_name = "${var.project_name}-compute-env"
  
  compute_resources {
    type = var.batch_compute_type
    
    max_vcpus = 16
    
    security_group_ids = [aws_security_group.batch_sg.id]
    subnets            = var.subnet_ids
  }
  
  service_role = aws_iam_role.batch_service_role.arn
  type         = "MANAGED"
}

# AWS Batch Job Queue
resource "aws_batch_job_queue" "factor_mining_queue" {
  name                 = "${var.project_name}-job-queue"
  state                = "ENABLED"
  priority             = 1
  compute_environments = [aws_batch_compute_environment.factor_mining_compute.arn]
}

# IAM Role for Batch Service
resource "aws_iam_role" "batch_service_role" {
  name = "${var.project_name}-batch-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "batch.amazonaws.com"
        }
      }
    ]
  })
}

# Attach AWS Batch Service Role policy
resource "aws_iam_role_policy_attachment" "batch_service_role_policy" {
  role       = aws_iam_role.batch_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

# Security Group for Batch
resource "aws_security_group" "batch_sg" {
  name        = "${var.project_name}-batch-sg"
  description = "Security group for Factor Mining Batch jobs"
  vpc_id      = var.vpc_id
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Step Function Definition
resource "aws_sfn_state_machine" "factor_mining_workflow" {
  name     = "${var.project_name}-workflow"
  role_arn = aws_iam_role.step_function_role.arn

  definition = <<EOF
{
  "Comment": "Factor Mining Workflow",
  "StartAt": "Initialize",
  "States": {
    "Initialize": {
      "Type": "Pass",
      "Result": {
        "DJIA_TICKERS": "${var.tickers}",
        "START_DATE": "${var.start_date}",
        "END_DATE": "${var.end_date}",
        "N": 5,
        "M": 6
      },
      "Next": "CalculateDateRanges"
    },
    "CalculateDateRanges": {
      "Type": "Task",
      "Resource": "${aws_lambda_function.calculate_date_ranges.arn}",
      "Next": "ProcessDateRanges"
    },
    "ProcessDateRanges": {
      "Type": "Map",
      "ItemsPath": "$.dateRanges",
      "Parameters": {
        "dateRange.$": "$$.Map.Item.Value",
        "tickers.$": "$.DJIA_TICKERS",
        "batch_no": 1
      },
      "MaxConcurrency": 10,
      "Iterator": {
        "StartAt": "ProcessDateRange",
        "States": {
          "ProcessDateRange": {
            "Type": "Task",
            "Resource": "arn:aws:states:::batch:submitJob.sync",
            "Parameters": {
              "JobName": "FactorMining-DateRange-Job",
              "JobQueue": "${aws_batch_job_queue.factor_mining_queue.arn}",
              "JobDefinition": "${aws_batch_job_definition.factor_mining_job.arn}",
              "Parameters": {
                "START_DATE.$": "$.dateRange.start",
                "END_DATE.$": "$.dateRange.end",
                "DJIA_TICKERS.$": "$.tickers",
                "BATCH_NO.$": "$.batch_no"
              }
            },
            "Retry": [
              {
                "ErrorEquals": ["States.ALL"],
                "IntervalSeconds": 60,
                "MaxAttempts": 3,
                "BackoffRate": 2.0
              }
            ],
            "End": true
          }
        }
      },
      "Next": "CalculateTickerGroups",
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "Next": "FailState"
        }
      ]
    },
    "CalculateTickerGroups": {
      "Type": "Task",
      "Resource": "${aws_lambda_function.calculate_ticker_groups.arn}",
      "Next": "ProcessTickerGroups"
    },
    "ProcessTickerGroups": {
      "Type": "Map",
      "ItemsPath": "$.tickerGroups",
      "Parameters": {
        "tickerGroup.$": "$$.Map.Item.Value",
        "startDate.$": "$.START_DATE",
        "endDate.$": "$.END_DATE",
        "batch_no": 2
      },
      "MaxConcurrency": 10,
      "Iterator": {
        "StartAt": "ProcessTickerGroup",
        "States": {
          "ProcessTickerGroup": {
            "Type": "Task",
            "Resource": "arn:aws:states:::batch:submitJob.sync",
            "Parameters": {
              "JobName": "FactorMining-TickerGroup-Job",
              "JobQueue": "${aws_batch_job_queue.factor_mining_queue.arn}",
              "JobDefinition": "${aws_batch_job_definition.factor_mining_job.arn}",
              "Parameters": {
                "START_DATE.$": "$.startDate",
                "END_DATE.$": "$.endDate",
                "DJIA_TICKERS.$": "$.tickerGroup",
                "BATCH_NO.$": "$.batch_no"
              }
            },
            "Retry": [
              {
                "ErrorEquals": ["States.ALL"],
                "IntervalSeconds": 60,
                "MaxAttempts": 3,
                "BackoffRate": 2.0
              }
            ],
            "End": true
          }
        }
      },
      "Next": "SuccessState",
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "Next": "FailState"
        }
      ]
    },
    "SuccessState": {
      "Type": "Succeed"
    },
    "FailState": {
      "Type": "Fail",
      "Error": "WorkflowFailed",
      "Cause": "One or more batch jobs failed"
    }
  }
}
EOF
}
