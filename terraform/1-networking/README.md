# Networking Infrastructure

This module provisions the base AWS networking components required for the factor mining platform.

## Components
- VPC with public and private subnets
- NAT Gateway for outbound connectivity
- Security Groups
- Route Tables

## Usage
1. Update `terraform.tfvars` with your specific configuration
2. Run `terraform init` and `terraform apply`

## Variables
| Name | Description | Type | Default |
|------|-------------|------|---------|
| vpc_cidr | CIDR block for VPC | string | "10.0.0.0/16" |
| region | AWS region | string | "us-east-1" |
| availability_zones | List of AZs | list(string) | ["us-east-1a", "us-east-1b"] |

## Outputs
- vpc_id
- private_subnet_ids
- public_subnet_ids
