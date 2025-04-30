# Factor Mining Platform

This repository contains infrastructure code and application code for a comprehensive factor mining platform on AWS.

## Architecture

The platform consists of several components:
1. **Data Collection**: Lambda functions to collect market data, SEC filings, and web search results
2. **Data Storage**: Clickhouse database and S3 buckets
3. **Processing**: AWS Step Functions and AWS Batch for factor mining
4. **Visualization**: Streamlit application for visualizing results

## Repository Structure

- `terraform/`: Terraform code for provisioning AWS resources
- `src/`: Application source code
- `scripts/`: Utility scripts
- `docs/`: Documentation

## Deployment

The platform is designed to be deployed in modules, allowing customers to choose which components to deploy.

### Prerequisites
- AWS account
- Terraform 1.0+
- Python 3.8+
- AWS CLI configured

### Deployment Steps

1. Deploy base networking:
   ```
   cd terraform/1-networking
   terraform init
   terraform apply
   ```

2. Deploy Clickhouse:
   ```
   cd terraform/2-clickhouse
   terraform init
   terraform apply
   ```

3. Deploy data collection modules as needed:
   - Market data
   - SEC data
   - Web search

4. Deploy factor mining infrastructure:
   ```
   cd terraform/6-factor-mining
   terraform init
   terraform apply
   ```

5. Deploy visualization:
   ```
   cd terraform/7-visualization
   terraform init
   terraform apply
   ```

## Development

### Local Development
1. Install dependencies: `pip install -r requirements.txt`
2. Run tests: `./scripts/test.sh`

### CI/CD
The repository includes GitHub Actions workflows for:
- Running tests
- Building Lambda packages
- Deploying infrastructure
