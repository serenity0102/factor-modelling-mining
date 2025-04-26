variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "lambda_runtime" {
  description = "Runtime for Lambda functions"
  type        = string
  default     = "python3.9"
}

variable "map_state_concurrency" {
  description = "Maximum concurrency for the Map state in Step Functions"
  type        = number
  default     = 30
}

variable "lambda_timeout" {
  description = "Default timeout for Lambda functions in seconds"
  type        = object({
    date_range_splitter = number
    process_year        = number
    consolidate_results = number
    split_tickers       = number
    process_single_ticker = number
    consolidate_ticker_results = number
  })
  default = {
    date_range_splitter = 30
    process_year        = 300
    consolidate_results = 60
    split_tickers       = 30
    process_single_ticker = 300
    consolidate_ticker_results = 60
  }
}

variable "enable_alerts" {
  description = "Enable alerting for the workflow"
  type        = bool
  default     = true
}

variable "alert_email" {
  description = "Email address to send alerts to"
  type        = string
  default     = "kenchowt@amazon.com"
}
