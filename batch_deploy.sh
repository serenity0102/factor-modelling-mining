#!/bin/bash
set -e

# Set AWS Profile
export AWS_PROFILE=factor

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "Terraform is not installed. Please install it first."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install it first."
    exit 1
fi

# Initialize Terraform with batch files
echo "Initializing Terraform with batch configuration files..."
terraform init

# Apply Terraform configuration
echo "Applying Terraform configuration..."
terraform apply -auto-approve -var-file=batch_variables.tfvars -state=batch.tfstate

# Get ECR repository URL
ECR_REPO_URL=$(terraform output -state=batch.tfstate -raw ecr_repository_url)
AWS_REGION=$(terraform output -state=batch.tfstate -raw aws_region 2>/dev/null || echo "us-east-1")

echo "ECR Repository URL: $ECR_REPO_URL"

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION --profile factor | docker login --username AWS --password-stdin $ECR_REPO_URL

# Build Docker image with platform specification
echo "Building Docker image for linux/amd64 platform..."
docker build --platform linux/amd64 -t factor-modeling:latest -f Dockerfile .

# Tag Docker image
echo "Tagging Docker image..."
docker tag factor-modeling:latest $ECR_REPO_URL:latest

# Push Docker image to ECR
echo "Pushing Docker image to ECR..."
docker push $ECR_REPO_URL:latest

echo "Deployment completed successfully!"
echo ""
echo "To submit a batch job, run:"
echo "aws batch submit-job --job-name factor-modeling-job-\$(date +%s) --job-queue factor-modeling-queue --job-definition factor-modeling-job --parameters batch_no=0,factor=ALL,tickers=ALL,start_date=2020-01-01,end_date=2025-03-31"
echo ""
echo "To submit specific batch jobs (0, 1, 2, or 3), run:"
echo "aws batch submit-job --job-name factor-modeling-job-\$(date +%s) --job-queue factor-modeling-queue --job-definition factor-modeling-job --parameters batch_no=1,factor=ALL,tickers=ALL,start_date=2020-01-01,end_date=2025-03-31"
echo ""
echo "To run a specific factor, use:"
echo "aws batch submit-job --job-name factor-modeling-job-\$(date +%s) --job-queue factor-modeling-queue --job-definition factor-modeling-job --parameters batch_no=0,factor=PEG,tickers=ALL,start_date=2020-01-01,end_date=2025-03-31"
