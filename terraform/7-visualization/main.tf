provider "aws" {
  region = var.aws_region
}

# Get existing VPC and subnet information
data "aws_vpc" "main" {
  filter {
    name   = "tag:Name"
    values = [var.vpc_name]
  }
}

data "aws_subnets" "all" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }
}


data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }
  filter {
    name   = "tag:Type"
    values = ["Public"]
  }
}

# Use the streamlit module to create the visualization application
module "factor_mining_visualization" {
  source = "../modules/streamlit"

  app_name        = "factor-mining-visualization"
  aws_region      = var.aws_region
  vpc_id          = data.aws_vpc.main.id
  subnet_ids      = data.aws_subnets.public.ids
  
  task_cpu        = var.task_cpu
  task_memory     = var.task_memory
  
  clickhouse_host     = var.clickhouse_host
  clickhouse_port     = var.clickhouse_port
  clickhouse_user     = var.clickhouse_user
  clickhouse_password = var.clickhouse_password
  clickhouse_database = var.clickhouse_database
  
  state_machine_arn = var.state_machine_arn
  
  service_desired_count = var.service_desired_count
  
  tags = {
    Environment = "production"
    Project     = "factor-mining"
    Module      = "visualization"
  }
}
