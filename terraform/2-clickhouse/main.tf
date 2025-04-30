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

module "clickhouse" {
  source = "../modules/clickhouse"

  vpc_id              = data.terraform_remote_state.networking.outputs.vpc_id
  subnet_ids          = data.terraform_remote_state.networking.outputs.private_subnet_ids
  instance_type       = var.instance_type
  volume_size         = var.volume_size
  clickhouse_version  = var.clickhouse_version
  project_name        = var.project_name
  environment         = var.environment
  key_name            = var.key_name
}
