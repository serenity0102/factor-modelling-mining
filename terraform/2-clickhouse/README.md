# Clickhouse Deployment

This module deploys a Clickhouse database on EC2 instances.

## Components
- EC2 instances for Clickhouse
- Security groups
- EBS volumes for data storage
- Optional: Auto Scaling Group for high availability

## Usage
1. Update `terraform.tfvars` with your specific configuration
2. Run `terraform init` and `terraform apply`

## Prerequisites
- Networking module must be deployed first

## Variables
| Name | Description | Type | Default |
|------|-------------|------|---------|
| instance_type | EC2 instance type | string | "r5.large" |
| volume_size | EBS volume size in GB | number | 100 |
| clickhouse_version | Clickhouse version | string | "22.3.13.80" |

## Outputs
- clickhouse_endpoint
- clickhouse_port
