provider "aws" {
  region = var.region
}

module "networking" {
  source = "../modules/networking"

  vpc_cidr            = var.vpc_cidr
  availability_zones  = var.availability_zones
  project_name        = var.project_name
  environment         = var.environment
}

# Output the created resources
output "vpc_id" {
  value = module.networking.vpc_id
}

output "private_subnet_ids" {
  value = module.networking.private_subnet_ids
}

output "public_subnet_ids" {
  value = module.networking.public_subnet_ids
}
