output "clickhouse_endpoint" {
  description = "Endpoint for Clickhouse"
  value       = module.clickhouse.clickhouse_endpoint
}

output "clickhouse_port" {
  description = "Port for Clickhouse"
  value       = module.clickhouse.clickhouse_port
}
