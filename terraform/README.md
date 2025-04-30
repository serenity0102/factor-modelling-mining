# Terraform Infrastructure Code

This directory contains all the Terraform code for provisioning the AWS infrastructure required for the factor mining platform.

## Structure

- `modules/`: Reusable Terraform modules
- `1-networking/`: Base networking infrastructure (VPC, subnets, etc.)
- `2-clickhouse/`: Clickhouse database deployment
- `3-market-data/`: Market data collection infrastructure
- `4-sec-data/`: SEC data collection infrastructure
- `5-web-search/`: Web search data collection infrastructure
- `6-factor-mining/`: Factor mining processing infrastructure
- `7-visualization/`: Visualization infrastructure

## Deployment Order

The modules should be deployed in the numbered order to ensure dependencies are satisfied:

1. Networking
2. Clickhouse
3-5. Data collection modules (can be deployed independently)
6. Factor mining
7. Visualization

## Best Practices

- Use remote state for production deployments
- Use variables for customization
- Follow the principle of least privilege for IAM roles
- Tag all resources appropriately
- Use consistent naming conventions
