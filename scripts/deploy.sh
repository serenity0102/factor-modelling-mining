#!/bin/bash

# Script to deploy the factor mining infrastructure

# Build Lambda packages
./scripts/build-lambdas.sh

# Deploy networking infrastructure
echo "Deploying networking infrastructure..."
cd terraform/1-networking
terraform init
terraform apply -auto-approve
cd ../..

# Deploy Clickhouse
echo "Deploying Clickhouse..."
cd terraform/2-clickhouse
terraform init
terraform apply -auto-approve
cd ../..

# Deploy factor mining infrastructure
echo "Deploying factor mining infrastructure..."
cd terraform/6-factor-mining
terraform init
terraform apply -auto-approve
cd ../..

echo "Deployment completed successfully!"
