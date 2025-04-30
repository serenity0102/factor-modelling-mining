output "step_function_arn" {
  description = "ARN of the Step Function state machine"
  value       = module.factor_mining.step_function_arn
}

output "batch_job_queue_arn" {
  description = "ARN of the AWS Batch job queue"
  value       = module.factor_mining.batch_job_queue_arn
}
