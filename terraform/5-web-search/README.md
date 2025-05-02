# Stock News Web Search

This project searches for stock news from the internet using the Tavily API for all 30 DJIA stocks and saves them to an S3 bucket. The solution is deployed as an AWS Lambda function that is triggered daily by EventBridge.

## Architecture

- **AWS Lambda**: Executes the Python code that searches for stock news and saves it to S3
- **Amazon EventBridge**: Triggers the Lambda function daily at midnight UTC for each stock ticker
- **Amazon S3**: Stores the fetched news data in JSON format
- **AWS Secrets Manager**: Securely stores the Tavily API key
- **IAM Roles and Policies**: Provides necessary permissions for Lambda to access S3 and Secrets Manager

## Features

- Searches for news for each stock ticker from the internet using Tavily API
- Filters news to include only today's news items
- Saves the filtered news to S3 with a structured path format
- Runs automatically every day for all 30 DJIA stocks

## Configuration

The solution is parameterized with the following variables:

- `tickers`: List of stock ticker symbols (default: DJIA 30 stocks)
- `s3_bucket_prefix`: Prefix for S3 bucket name (default: stock-news-data)
- `tavily_api_key`: API key for Tavily web search service (required)

## Deployment

The infrastructure is deployed using Terraform. Before deploying, you need to set the Tavily API key as an environment variable:

```bash
export TF_VAR_tavily_api_key="your-tavily-api-key"
```

Then run:

```bash
terraform init
terraform apply
```

The deployment creates:

1. S3 bucket for storing news data
2. Secrets Manager secret for storing the Tavily API key
3. Lambda function with necessary IAM roles and policies
4. EventBridge rule to trigger the Lambda function daily for each ticker

## Usage

The Lambda function is triggered automatically every day at midnight UTC for each ticker. It will:

1. Search for news about each stock ticker from the internet using Tavily API
2. Filter the news to include only items published on the current date
3. Save the filtered news to the S3 bucket in the following path format:
   `{ticker}/{date}/market_news.json`

## DJIA 30 Stocks

The solution is configured to fetch news for the following 30 DJIA stocks:

- AAPL (Apple)
- AMGN (Amgen)
- AMZN (Amazon)
- AXP (American Express)
- BA (Boeing)
- CAT (Caterpillar)
- CRM (Salesforce)
- CSCO (Cisco)
- CVX (Chevron)
- DIS (Disney)
- GS (Goldman Sachs)
- HD (Home Depot)
- HON (Honeywell)
- IBM (IBM)
- JNJ (Johnson & Johnson)
- JPM (JPMorgan Chase)
- KO (Coca-Cola)
- MCD (McDonald's)
- MMM (3M)
- MRK (Merck)
- MSFT (Microsoft)
- NKE (Nike)
- NVDA (NVIDIA)
- PG (Procter & Gamble)
- SHW (Sherwin-Williams)
- TRV (Travelers)
- UNH (UnitedHealth)
- V (Visa)
- VZ (Verizon)
- WMT (Walmart)

## Local Development

To run the Lambda function locally:

```bash
python lambda_function.py
```

Make sure to set the required environment variables:
- `S3_BUCKET`: Name of the S3 bucket
- `DEFAULT_TICKER`: Default stock ticker symbol
- `TAVILY_API_KEY_NAME`: Name of the Secrets Manager secret containing the Tavily API key
