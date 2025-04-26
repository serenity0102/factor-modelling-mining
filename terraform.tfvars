aws_region = "us-east-1"
lambda_runtime = "python3.9"
map_state_concurrency = 30

lambda_timeout = {
  date_range_splitter = 30
  process_year = 300
  consolidate_results = 60
  split_tickers = 30
  process_single_ticker = 300
  consolidate_ticker_results = 60
}

enable_alerts = true
alert_email = "alerts@example.com"  # Replace with your actual email
