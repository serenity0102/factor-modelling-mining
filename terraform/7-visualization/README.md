# Factor Mining Visualization Infrastructure

This directory contains Terraform configuration for deploying the Factor Mining Visualization application to AWS.

## Architecture

The application is deployed as a containerized Streamlit application running on AWS Fargate with the following components:

- Amazon ECR repository for storing the Docker image
- ECS Cluster and Service for running the application
- Application Load Balancer for routing traffic
- IAM roles and policies for accessing AWS resources
- CloudWatch Log Group for logging

## Prerequisites

- AWS profile with right permissions
- Terraform 1.0+
- Docker installed locally
- Existing VPC with public subnets

## Deployment Steps

1. Run the deployment script:

```bash
# Navigate to the terraform directory
cd terraform/7-visualization

# Run the deployment script
./deploy.sh
```

The script will:
- Apply the Terraform configuration
- Build and push the Docker image to ECR
- Deploy the application to ECS Fargate
- Output the URL to access the application

## Configuration

You can customize the deployment by modifying the variables in `variables.tf` or by providing a `.tfvars` file.

Example `terraform.tfvars`:

```hcl
aws_region = "us-east-1"
clickhouse_host = ""
clickhouse_port = 9000
clickhouse_user = "default"
clickhouse_password = ""
clickhouse_database = "factor_model_tick_data_database"
task_cpu = "2048"
task_memory = "4096"
service_desired_count = 1
```

## Manual Deployment

If you prefer to deploy manually:

1. Initialize and apply Terraform:
```bash
terraform init
terraform apply
```

2. Build and push the Docker image:
```bash
# Get the ECR repository URL
ECR_REPO=$(terraform output -raw ecr_repository_url)

# Build the Docker image
cd ../../src/visualization
docker build -t factor-mining-visualization .

# Log in to ECR
aws ecr get-login-password --region us-east-1 --profile factor | docker login --username AWS --password-stdin $ECR_REPO

# Tag and push the image
docker tag factor-mining-visualization:latest $ECR_REPO:latest
docker push $ECR_REPO:latest
```

3. Force a new deployment:
```bash
CLUSTER_NAME=$(terraform -chdir=../../terraform/7-visualization output -raw ecs_cluster_name)
SERVICE_NAME=$(terraform -chdir=../../terraform/7-visualization output -raw ecs_service_name)
aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --force-new-deployment --region us-east-1 --profile factor
```

## Cleanup

To destroy all resources created by this configuration:

```bash
terraform destroy
```
