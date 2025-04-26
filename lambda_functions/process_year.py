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
    Process data for a specific year.
    
    Input:
    {
        "year": 2000,
        "additionalParams": {
            "param1": "value1",
            "param2": "value2"
        }
    }
    
    Output:
    {
        "year": 2000,
        "result": {
            "metrics": {...},
            "statistics": {...}
        }
    }
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        year = event.get('year')
        additional_params = event.get('additionalParams', {})
        
        logger.info(f"Processing data for year {year} with params: {additional_params}")
        
        # Simulate processing time
        time.sleep(2)
        
        # This is where you would implement your actual backtesting logic for the year
        # For example, loading data, running models, calculating metrics, etc.
        
        # Sample result - replace with your actual processing logic
        result = {
            "year": year,
            "result": {
                "metrics": {
                    "sharpeRatio": 1.2 + (year - 2000) * 0.05,
                    "maxDrawdown": 0.15 - (year - 2000) * 0.01,
                    "annualReturn": 0.08 + (year - 2000) * 0.005
                },
                "statistics": {
                    "winRate": 0.55 + (year - 2000) * 0.01,
                    "tradeCount": 250 + (year - 2000) * 10
                }
            }
        }
        
        # Publish success metric
        publish_metric('ProcessYearSuccess', 1, {'Year': str(year)})
        
        logger.info(f"Completed processing for year {year}")
        
        return result
    except Exception as e:
        error_msg = f"Error processing year {event.get('year', 'unknown')}: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Publish error metric
        publish_metric('ProcessYearError', 1, {'Year': str(event.get('year', 'unknown'))})
        
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
        subject = f"Backtesting Alert: Year Processing Error"
        
        message_body = f"""
        ALERT: Error in Year Processing Lambda
        
        Timestamp: {timestamp}
        Function: ProcessYearFunction
        Year: {event_data.get('year', 'unknown')}
        
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
