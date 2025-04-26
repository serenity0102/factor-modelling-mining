# CloudWatch Dashboard for Backtesting Workflow
resource "aws_cloudwatch_dashboard" "backtesting_dashboard" {
  dashboard_name = "BacktestingWorkflowDashboard"
  
  dashboard_body = jsonencode({
    widgets = [
      # Step Functions Execution Metrics
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/States", "ExecutionsStarted", "StateMachineArn", aws_sfn_state_machine.backtesting_workflow.arn],
            ["AWS/States", "ExecutionsSucceeded", "StateMachineArn", aws_sfn_state_machine.backtesting_workflow.arn],
            ["AWS/States", "ExecutionsFailed", "StateMachineArn", aws_sfn_state_machine.backtesting_workflow.arn],
            ["AWS/States", "ExecutionsTimedOut", "StateMachineArn", aws_sfn_state_machine.backtesting_workflow.arn]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Step Functions Executions"
          period  = 300
          stat    = "Sum"
        }
      },
      
      # Year Processing Metrics
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["BacktestingWorkflow", "ProcessYearSuccess", "Service", "BacktestingWorkflow"],
            ["BacktestingWorkflow", "ProcessYearError", "Service", "BacktestingWorkflow"]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Year Processing Metrics"
          period  = 300
          stat    = "Sum"
        }
      },
      
      # Ticker Processing Metrics
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["BacktestingWorkflow", "ProcessTickerSuccess", "Service", "BacktestingWorkflow"],
            ["BacktestingWorkflow", "ProcessTickerError", "Service", "BacktestingWorkflow"]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Ticker Processing Metrics"
          period  = 300
          stat    = "Sum"
        }
      },
      
      # Lambda Duration Metrics
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Lambda", "Duration", "FunctionName", aws_lambda_function.process_year.function_name, { "label": "Process Year" }],
            ["AWS/Lambda", "Duration", "FunctionName", aws_lambda_function.process_single_ticker.function_name, { "label": "Process Ticker" }],
            ["AWS/Lambda", "Duration", "FunctionName", aws_lambda_function.consolidate_results.function_name, { "label": "Consolidate Results" }],
            ["AWS/Lambda", "Duration", "FunctionName", aws_lambda_function.consolidate_ticker_results.function_name, { "label": "Consolidate Ticker Results" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Lambda Duration"
          period  = 300
          stat    = "Average"
        }
      },
      
      # Lambda Error Metrics
      {
        type   = "metric"
        x      = 0
        y      = 12
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Lambda", "Errors", "FunctionName", aws_lambda_function.process_year.function_name, { "label": "Process Year" }],
            ["AWS/Lambda", "Errors", "FunctionName", aws_lambda_function.process_single_ticker.function_name, { "label": "Process Ticker" }],
            ["AWS/Lambda", "Errors", "FunctionName", aws_lambda_function.consolidate_results.function_name, { "label": "Consolidate Results" }],
            ["AWS/Lambda", "Errors", "FunctionName", aws_lambda_function.consolidate_ticker_results.function_name, { "label": "Consolidate Ticker Results" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Lambda Errors"
          period  = 300
          stat    = "Sum"
        }
      },
      
      # Alarm Status
      {
        type   = "alarm"
        x      = 12
        y      = 12
        width  = 12
        height = 6
        properties = {
          alarms = var.enable_alerts ? [
            aws_cloudwatch_metric_alarm.year_processing_errors[0].arn,
            aws_cloudwatch_metric_alarm.ticker_processing_errors[0].arn
          ] : []
          title = "Backtesting Alarms"
        }
      }
    ]
  })
}
