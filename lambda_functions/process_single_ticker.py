import json
import logging
import traceback
import os
import boto3
import time
from datetime import datetime

# Configure logging
logger = logging.getLogger()
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logger.setLevel(getattr(logging, log_level))

# Initialize CloudWatch metrics client
cloudwatch = boto3.client('cloudwatch')
sns = boto3.client('sns')
SNS_TOPIC_ARN = os.environ.get('ALERT_SNS_TOPIC_ARN', '')

def lambda_handler(event, context):
    """
    Process data for a single ticker.
    
    Input:
    {
        "ticker": "AAPL",
        "additionalParams": {
            "param1": "value1",
            "param2": "value2"
        }
    }
    
    Output:
    {
        "ticker": "AAPL",
        "result": {
            "return": 0.12,
            "volatility": 0.18,
            "sharpeRatio": 1.5,
            "maxDrawdown": 0.08,
            "winRate": 0.62,
            "tradeCount": 320
        }
    }
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        ticker = event.get('ticker')
        additional_params = event.get('additionalParams', {})
        
        logger.info(f"Processing data for ticker {ticker} with params: {additional_params}")
        
        # Simulate processing time
        time.sleep(1)
        
        # This is where you would implement your actual ticker-specific backtesting logic
        # For example, loading data, running models, calculating metrics, etc.
        
        # Generate some sample metrics based on the ticker string to simulate different results
        # In a real implementation, this would be replaced with actual analysis
        ticker_ord_sum = sum(ord(c) for c in ticker)
        seed = ticker_ord_sum / 1000.0
        
        result = {
            "ticker": ticker,
            "result": {
                "return": 0.08 + (seed * 0.05),
                "volatility": 0.22 - (seed * 0.04),
                "sharpeRatio": 1.2 + (seed * 0.3),
                "maxDrawdown": 0.15 - (seed * 0.07),
                "winRate": 0.55 + (seed * 0.1),
                "tradeCount": 250 + int(seed * 100)
            }
        }
        
        # Publish success metric
        publish_metric('ProcessTickerSuccess', 1, {'Ticker': ticker})
        
        logger.info(f"Completed processing for ticker {ticker}")
        
        return result
    except Exception as e:
        error_msg = f"Error processing ticker {event.get('ticker', 'unknown')}: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Publish error metric
        publish_metric('ProcessTickerError', 1, {'Ticker': str(event.get('ticker', 'unknown'))})
        
        # Send alert notification
        if SNS_TOPIC_ARN:
            send_alert(error_msg, event)
        
        # Re-raise the exception to mark the Lambda execution as failed
        raise

def publish_metric(metric_name, value, dimensions):
    """Publish a metric to CloudWatch"""
    try:
        dimension_list = [{'Name': k, 'Value': v} for k, v in dimensions.items()]
        cloudwatch.put_metric_data(
            Namespace='BacktestingWorkflow',
            MetricData=[
                {
                    'MetricName': metric_name,
                    'Dimensions': dimension_list,
                    'Value': value,
                    'Unit': 'Count'
                }
            ]
        )
    except Exception as e:
        logger.error(f"Failed to publish metric {metric_name}: {str(e)}")

def send_alert(message, event_data):
    """Send an alert notification via SNS"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"Backtesting Alert: Ticker Processing Error"
        
        message_body = f"""
        ALERT: Error in Ticker Processing Lambda
        
        Timestamp: {timestamp}
        Function: ProcessSingleTickerFunction
        Ticker: {event_data.get('ticker', 'unknown')}
        
        Error Message: {message}
        
        Event Data: {json.dumps(event_data, indent=2)}
        """
        
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message_body
        )
    except Exception as e:
        logger.error(f"Failed to send alert: {str(e)}")
