output "clickhouse_endpoint" {
  description = "Endpoint for Clickhouse"
  value       = aws_instance.clickhouse.public_dns
}

output "clickhouse_port" {
  description = "Port for Clickhouse"
  value       = 8123
}
