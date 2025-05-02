variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
}

variable "vpc_name" {
  description = "Name of the existing VPC"
  type        = string
}

variable "clickhouse_host" {
  description = "Clickhouse host address"
  type        = string
}

variable "clickhouse_port" {
  description = "Clickhouse port"
  type        = number
  default     = 9000
}

variable "clickhouse_user" {
  description = "Clickhouse username"
  type        = string
  default     = "default"
}

variable "clickhouse_password" {
  description = "Clickhouse password"
  type        = string
  sensitive   = true
}

variable "clickhouse_database" {
  description = "Clickhouse database name"
  type        = string
  default     = "factor_model_tick_data_database"
}

variable "state_machine_arn" {
  description = "ARN of the Step Function state machine"
  type        = string
}

variable "task_cpu" {
  description = "CPU units for the ECS task"
  type        = string
  default     = "1024"
}

variable "task_memory" {
  description = "Memory for the ECS task"
  type        = string
  default     = "2048"
}

variable "service_desired_count" {
  description = "Desired count of ECS tasks"
  type        = number
  default     = 1
}

variable "app_name" {
  description = "Name of the application"
  type        = string
  default     = "factor-mining-visualization"
}
