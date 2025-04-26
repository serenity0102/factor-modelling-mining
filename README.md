# Backtesting Step Functions Workflow

This project implements an AWS Step Functions workflow for backtesting financial models across multiple years or tickers. The workflow takes either a date range or a list of tickers as input, processes each item in parallel, and then consolidates the results.

## Architecture

The workflow consists of the following components:

1. **Input Processing**:
   - **Date Range Splitter Lambda**: Splits the input date range into individual years
   - **Split Tickers Lambda**: Prepares individual ticker items for processing

2. **Parallel Processing**:
   - **Process Year Lambda**: Processes data for a specific year
   - **Process Single Ticker Lambda**: Processes data for a specific ticker

3. **Results Consolidation**:
   - **Consolidate Results Lambda**: Combines results from all years into a final summary
   - **Consolidate Ticker Results Lambda**: Combines results from all tickers into a final summary

4. **Step Functions State Machine**: Orchestrates the entire workflow with a Choice state to handle different input types

## Workflow Steps

1. **CheckInputType**: Determines whether the input contains years or tickers
2. **SplitDateRange/ProcessTickers**: Prepares individual items for processing
3. **ProcessYears/ProcessTickersMap**: Uses a Map state to process each item in parallel
4. **ConsolidateResults/ConsolidateTickerResults**: Combines the results into a final summary

## Deployment

### Prerequisites

- Terraform installed
- AWS CLI configured with appropriate credentials
- Python 3.9 or later

### Setup

1. Clone this repository
2. Navigate to the project directory
3. Create Lambda function ZIP files:

```bash
mkdir -p lambda_functions
cd lambda_functions

# Create ZIP for Lambda functions
zip date_range_splitter.zip date_range_splitter.py
zip process_year.zip process_year.py
zip consolidate_results.zip consolidate_results.py
zip split_tickers.zip split_tickers.py
zip process_single_ticker.zip process_single_ticker.py
zip consolidate_ticker_results.zip consolidate_ticker_results.py
zip process_tickers.zip process_tickers.py

cd ..
```

### Configuration

You can customize the deployment by modifying the `terraform.tfvars` file:

```hcl
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
```

### Deploy

```bash
terraform init
terraform plan
terraform apply
```

## Usage

To execute the Step Functions workflow, you can use the AWS CLI or AWS Console.

### Using AWS CLI for Year-Based Processing

```bash
aws stepfunctions start-execution \
  --state-machine-arn <state_machine_arn> \
  --input '{
    "startYear": 2000,
    "endYear": 2010,
    "additionalParams": {
      "param1": "value1",
      "param2": "value2"
    }
  }'
```

### Using AWS CLI for Ticker-Based Processing

```bash
aws stepfunctions start-execution \
  --state-machine-arn <state_machine_arn> \
  --input '{
    "tickers": ["AAPL", "MSFT", "GOOG", "AMZN", "META"],
    "additionalParams": {
      "param1": "value1",
      "param2": "value2"
    }
  }'
```

## Input/Output Formats

### Year-Based Input

```json
{
  "startYear": 2000,
  "endYear": 2010,
  "additionalParams": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

### Year-Based Output

```json
{
  "startYear": 2000,
  "endYear": 2010,
  "additionalParams": {...},
  "years": [2000, 2001, 2002, ...],
  "yearResults": [
    {
      "year": 2000,
      "result": {
        "metrics": {...},
        "statistics": {...}
      }
    },
    // ... results for other years
  ],
  "finalResult": {
    "summary": {
      "averageMetrics": {...},
      "yearlyResults": [...]
    }
  }
}
```

### Ticker-Based Input

```json
{
  "tickers": ["AAPL", "MSFT", "GOOG", "AMZN", "META"],
  "additionalParams": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

### Ticker-Based Output

```json
{
  "tickers": [
    {"ticker": "AAPL", "additionalParams": {...}},
    // ... other tickers
  ],
  "additionalParams": {...},
  "tickerResults": [
    {
      "ticker": "AAPL",
      "result": {
        "return": 0.12,
        "volatility": 0.18,
        // ... other metrics
      }
    },
    // ... results for other tickers
  ],
  "finalResult": {
    "summary": {
      "averageMetrics": {...},
      "tickerResults": [...]
    }
  }
}
```

## Customization

You can customize the workflow by:

1. Modifying the Lambda functions to implement your specific backtesting logic
2. Adjusting the concurrency in the Map state via the `map_state_concurrency` variable
3. Changing Lambda function timeouts via the `lambda_timeout` variable
4. Adding error handling and retry logic
5. Extending the workflow with additional states for pre-processing or post-processing

## Clean Up

To remove all resources:

```bash
terraform destroy
```
