output "ecr_repository_url" {
  value       = module.factor_mining_visualization.ecr_repository_url
  description = "URL of the ECR repository"
}

output "ecs_cluster_name" {
  value       = module.factor_mining_visualization.ecs_cluster_name
  description = "Name of the ECS cluster"
}

output "ecs_service_name" {
  value       = module.factor_mining_visualization.ecs_service_name
  description = "Name of the ECS service"
}

output "load_balancer_dns" {
  value       = module.factor_mining_visualization.load_balancer_dns
  description = "DNS name of the load balancer"
}

output "application_url" {
  value       = module.factor_mining_visualization.application_url
  description = "URL to access the application"
}
