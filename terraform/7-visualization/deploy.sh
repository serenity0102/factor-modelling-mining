#!/bin/bash

# Exit on error
set -e

# Set AWS profile
export AWS_PROFILE=factor

# Initialize Terraform if needed
terraform init

# Apply Terraform configuration
terraform apply -auto-approve

# Get ECR repository URL
ECR_REPO=$(terraform output -raw ecr_repository_url)
echo "ECR Repository: $ECR_REPO"

# Navigate to the application directory
cd ../../src/visualization

# Build Docker image for AMD64 platform (what AWS ECS uses)
echo "Building Docker image for AMD64 platform..."
docker buildx create --use --name builder || true
docker buildx use builder
docker buildx build --platform linux/amd64 -t factor-mining-visualization:latest .

# Log in to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REPO

# Tag and push the image
echo "Tagging and pushing image to ECR..."
docker buildx build --platform linux/amd64 -t $ECR_REPO:\latest --push .

# Force new deployment of the ECS service
echo "Updating ECS service..."
CLUSTER_NAME=$(terraform -chdir=../../terraform/7-visualization output -raw ecs_cluster_name)
SERVICE_NAME=$(terraform -chdir=../../terraform/7-visualization output -raw ecs_service_name)
aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --force-new-deployment --region us-east-1

echo "Deployment completed!"
echo "Application URL: $(terraform -chdir=../../terraform/7-visualization output -raw application_url)"
echo "It may take a few minutes for the new container to start and the health checks to pass."
