provider "aws" {
  region = var.region
}

# Get networking outputs from remote state
data "terraform_remote_state" "networking" {
  backend = "local"
  config = {
    path = "../1-networking/terraform.tfstate"
  }
}

# Get clickhouse outputs from remote state
data "terraform_remote_state" "clickhouse" {
  backend = "local"
  config = {
    path = "../2-clickhouse/terraform.tfstate"
  }
}

module "factor_mining" {
  source = "../modules/step-functions"

  vpc_id                = data.terraform_remote_state.networking.outputs.vpc_id
  subnet_ids            = data.terraform_remote_state.networking.outputs.private_subnet_ids
  clickhouse_endpoint   = data.terraform_remote_state.clickhouse.outputs.clickhouse_endpoint
  clickhouse_port       = data.terraform_remote_state.clickhouse.outputs.clickhouse_port
  batch_compute_type    = var.batch_compute_type
  batch_vcpus           = var.batch_vcpus
  batch_memory          = var.batch_memory
  tickers               = var.tickers
  start_date            = var.start_date
  end_date              = var.end_date
  project_name          = var.project_name
  environment           = var.environment
  ecr_repository_url    = var.ecr_repository_url
}
