output "state_machine_arn" {
  description = "ARN of the Step Functions state machine"
  value       = aws_sfn_state_machine.backtesting_workflow.arn
}

output "state_machine_name" {
  description = "Name of the Step Functions state machine"
  value       = aws_sfn_state_machine.backtesting_workflow.name
}

output "lambda_functions" {
  description = "ARNs of the Lambda functions"
  value = {
    date_range_splitter = aws_lambda_function.date_range_splitter.arn
    process_year        = aws_lambda_function.process_year.arn
    consolidate_results = aws_lambda_function.consolidate_results.arn
  }
}
