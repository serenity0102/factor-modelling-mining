variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "subnet_ids" {
  description = "IDs of the subnets"
  type        = list(string)
}

variable "instance_type" {
  description = "EC2 instance type for Clickhouse"
  type        = string
  default     = "r5.large"
}

variable "volume_size" {
  description = "EBS volume size in GB"
  type        = number
  default     = 100
}

variable "clickhouse_version" {
  description = "Clickhouse version"
  type        = string
  default     = "22.3.13.80"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "factor-mining"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "key_name" {
  description = "SSH key name"
  type        = string
  default     = null
}
