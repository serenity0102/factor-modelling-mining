provider "aws" {
  region = var.aws_region
}

# Lambda function to split tickers list
resource "aws_lambda_function" "split_tickers" {
  function_name = "SplitTickersFunction"
  role          = aws_iam_role.lambda_role.arn
  handler       = "split_tickers.lambda_handler"
  runtime       = var.lambda_runtime
  filename      = "${path.module}/lambda_functions/split_tickers.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda_functions/split_tickers.zip")
  timeout       = var.lambda_timeout.split_tickers

  environment {
    variables = {
      LOG_LEVEL = "INFO"
    }
  }
}

# Lambda function to process a single ticker
resource "aws_lambda_function" "process_single_ticker" {
  function_name = "ProcessSingleTickerFunction"
  role          = aws_iam_role.lambda_role.arn
  handler       = "process_single_ticker.lambda_handler"
  runtime       = var.lambda_runtime
  filename      = "${path.module}/lambda_functions/process_single_ticker.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda_functions/process_single_ticker.zip")
  timeout       = var.lambda_timeout.process_single_ticker

  environment {
    variables = {
      LOG_LEVEL = "INFO"
    }
  }
}

# Lambda function to consolidate ticker results
resource "aws_lambda_function" "consolidate_ticker_results" {
  function_name = "ConsolidateTickerResultsFunction"
  role          = aws_iam_role.lambda_role.arn
  handler       = "consolidate_ticker_results.lambda_handler"
  runtime       = var.lambda_runtime
  filename      = "${path.module}/lambda_functions/consolidate_ticker_results.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda_functions/consolidate_ticker_results.zip")
  timeout       = var.lambda_timeout.consolidate_ticker_results

  environment {
    variables = {
      LOG_LEVEL = "INFO"
    }
  }
}

# SNS Topic for alerts
resource "aws_sns_topic" "backtesting_alerts" {
  name = "BacktestingAlerts"
}

# SNS Topic Subscription for email alerts
resource "aws_sns_topic_subscription" "email_subscription" {
  count     = var.enable_alerts && var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.backtesting_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# CloudWatch Alarm for Year Processing Errors
resource "aws_cloudwatch_metric_alarm" "year_processing_errors" {
  count               = var.enable_alerts ? 1 : 0
  alarm_name          = "BacktestingYearProcessingErrors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ProcessYearError"
  namespace           = "BacktestingWorkflow"
  period              = 60
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "This alarm monitors errors in year processing"
  alarm_actions       = [aws_sns_topic.backtesting_alerts.arn]
  
  dimensions = {
    Service = "BacktestingWorkflow"
  }
}

# CloudWatch Alarm for Ticker Processing Errors
resource "aws_cloudwatch_metric_alarm" "ticker_processing_errors" {
  count               = var.enable_alerts ? 1 : 0
  alarm_name          = "BacktestingTickerProcessingErrors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ProcessTickerError"
  namespace           = "BacktestingWorkflow"
  period              = 60
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "This alarm monitors errors in ticker processing"
  alarm_actions       = [aws_sns_topic.backtesting_alerts.arn]
  
  dimensions = {
    Service = "BacktestingWorkflow"
  }
}

# Lambda function to process tickers
resource "aws_lambda_function" "process_tickers" {
  function_name = "ProcessTickersFunction"
  role          = aws_iam_role.lambda_role.arn
  handler       = "process_tickers.lambda_handler"
  runtime       = var.lambda_runtime
  filename      = "${path.module}/lambda_functions/process_tickers.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda_functions/process_tickers.zip")
  timeout       = var.lambda_timeout.process_year  # Using the same timeout as process_year

  environment {
    variables = {
      LOG_LEVEL = "INFO"
    }
  }
}

# IAM Role for Lambda functions
resource "aws_iam_role" "lambda_role" {
  name = "backtesting_lambda_role"

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
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda function to split date range into years
resource "aws_lambda_function" "date_range_splitter" {
  function_name = "DateRangeSplitterFunction"
  role          = aws_iam_role.lambda_role.arn
  handler       = "date_range_splitter.lambda_handler"
  runtime       = var.lambda_runtime
  filename      = "${path.module}/lambda_functions/date_range_splitter.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda_functions/date_range_splitter.zip")
  timeout       = var.lambda_timeout.date_range_splitter

  environment {
    variables = {
      LOG_LEVEL = "INFO"
    }
  }
}

# Lambda function to process a single year
resource "aws_lambda_function" "process_year" {
  function_name = "ProcessYearFunction"
  role          = aws_iam_role.lambda_role.arn
  handler       = "process_year.lambda_handler"
  runtime       = var.lambda_runtime
  filename      = "${path.module}/lambda_functions/process_year.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda_functions/process_year.zip")
  timeout       = var.lambda_timeout.process_year  # Adjust based on your processing needs

  environment {
    variables = {
      LOG_LEVEL = "INFO"
    }
  }
}

# Lambda function to consolidate results
resource "aws_lambda_function" "consolidate_results" {
  function_name = "ConsolidateResultsFunction"
  role          = aws_iam_role.lambda_role.arn
  handler       = "consolidate_results.lambda_handler"
  runtime       = var.lambda_runtime
  filename      = "${path.module}/lambda_functions/consolidate_results.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda_functions/consolidate_results.zip")
  timeout       = var.lambda_timeout.consolidate_results

  environment {
    variables = {
      LOG_LEVEL = "INFO"
    }
  }
}

# IAM Role for Step Functions
resource "aws_iam_role" "step_function_role" {
  name = "backtesting_step_function_role"

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

# Policy to allow Step Functions to invoke Lambda
resource "aws_iam_policy" "step_function_lambda_invoke" {
  name        = "StepFunctionLambdaInvokePolicy"
  description = "Allow Step Functions to invoke Lambda functions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "lambda:InvokeFunction"
        ]
        Effect = "Allow"
        Resource = [
          aws_lambda_function.date_range_splitter.arn,
          aws_lambda_function.process_year.arn,
          aws_lambda_function.consolidate_results.arn,
          aws_lambda_function.process_tickers.arn,
          aws_lambda_function.split_tickers.arn,
          aws_lambda_function.process_single_ticker.arn,
          aws_lambda_function.consolidate_ticker_results.arn
        ]
      }
    ]
  })
}

# Attach policy to Step Functions role
resource "aws_iam_role_policy_attachment" "step_function_lambda_invoke" {
  role       = aws_iam_role.step_function_role.name
  policy_arn = aws_iam_policy.step_function_lambda_invoke.arn
}

# Step Functions State Machine
resource "aws_sfn_state_machine" "backtesting_workflow" {
  name     = "BacktestingWorkflow"
  role_arn = aws_iam_role.step_function_role.arn
  
  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.step_function_logs.arn}:*"
    include_execution_data = true
    level                  = "ALL"
  }

  definition = jsonencode({
    Comment = "Backtesting Workflow"
    StartAt = "CheckInputType"
    States = {
      CheckInputType = {
        Type = "Choice"
        Choices = [
          {
            Variable = "$.startYear"
            IsPresent = true
            Next = "SplitDateRange"
          },
          {
            Variable = "$.tickers"
            IsPresent = true
            Next = "ProcessTickers"
          }
        ],
        Default = "HandleInvalidInput"
      },
      HandleInvalidInput = {
        Type = "Fail"
        Error = "InvalidInput"
        Cause = "Input must contain either 'startYear' and 'endYear' OR 'tickers'"
      },
      ProcessTickers = {
        Type = "Task"
        Resource = aws_lambda_function.split_tickers.arn
        ResultPath = "$.tickers"
        Next = "ProcessTickersMap"
      },
      ProcessTickersMap = {
        Type = "Map"
        ItemsPath = "$.tickers"
        Parameters = {
          "ticker.$" = "$$.Map.Item.Value.ticker"
          "additionalParams.$" = "$$.Map.Item.Value.additionalParams"
        }
        ResultPath = "$.tickerResults"
        MaxConcurrency = var.map_state_concurrency
        Next = "ConsolidateTickerResults"
        Iterator = {
          StartAt = "ProcessSingleTicker"
          States = {
            ProcessSingleTicker = {
              Type = "Task"
              Resource = aws_lambda_function.process_single_ticker.arn
              End = true
            }
          }
        }
      },
      ConsolidateTickerResults = {
        Type = "Task"
        Resource = aws_lambda_function.consolidate_ticker_results.arn
        Parameters = {
          "tickerResults.$" = "$.tickerResults"
        }
        ResultPath = "$.finalResult"
        End = true
      },
      SplitDateRange = {
        Type = "Task"
        Resource = aws_lambda_function.date_range_splitter.arn
        Parameters = {
          "startYear.$" = "$.startYear"
          "endYear.$" = "$.endYear"
        }
        ResultPath = "$.years"
        Next = "ProcessYears"
      }
      ProcessYears = {
        Type = "Map"
        ItemsPath = "$.years"
        Parameters = {
          "year.$" = "$$.Map.Item.Value"
          "additionalParams.$" = "$.additionalParams"
        }
        ResultPath = "$.yearResults"
        MaxConcurrency = var.map_state_concurrency
        Next = "ConsolidateResults"
        Iterator = {
          StartAt = "ProcessSingleYear"
          States = {
            ProcessSingleYear = {
              Type = "Task"
              Resource = aws_lambda_function.process_year.arn
              End = true
            }
          }
        }
      }
      ConsolidateResults = {
        Type = "Task"
        Resource = aws_lambda_function.consolidate_results.arn
        Parameters = {
          "yearResults.$" = "$.yearResults"
        }
        ResultPath = "$.finalResult"
        End = true
      }
    }
  })
}

# CloudWatch Log Group for Step Functions
resource "aws_cloudwatch_log_group" "step_function_logs" {
  name              = "/aws/states/BacktestingWorkflow"
  retention_in_days = 14
}

# Additional permissions for Step Functions to write logs
resource "aws_iam_policy" "step_function_logging" {
  name        = "StepFunctionLoggingPolicy"
  description = "Allow Step Functions to write logs to CloudWatch"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogDelivery",
          "logs:GetLogDelivery",
          "logs:UpdateLogDelivery",
          "logs:DeleteLogDelivery",
          "logs:ListLogDeliveries",
          "logs:PutLogEvents",
          "logs:PutResourcePolicy",
          "logs:DescribeResourcePolicies",
          "logs:DescribeLogGroups",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# Attach logging policy to Step Functions role
resource "aws_iam_role_policy_attachment" "step_function_logging" {
  role       = aws_iam_role.step_function_role.name
  policy_arn = aws_iam_policy.step_function_logging.arn
}
