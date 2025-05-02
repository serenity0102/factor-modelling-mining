terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.67"  # Using a slightly older, stable version
    }
  }
  required_version = ">= 1.0"
}
