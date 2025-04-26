import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Process data for a list of tickers.
    
    Input:
    {
        "tickers": ["AAPL", "MSFT", "GOOG"],
        "additionalParams": {
            "param1": "value1",
            "param2": "value2"
        }
    }
    
    Output:
    {
        "tickers": ["AAPL", "MSFT", "GOOG"],
        "result": {
            "metrics": {...},
            "statistics": {...}
        }
    }
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    tickers = event.get('tickers', [])
    additional_params = event.get('additionalParams', {})
    
    logger.info(f"Processing data for tickers: {tickers} with params: {additional_params}")
    
    # This is where you would implement your actual ticker processing logic
    # For example, loading data, running models, calculating metrics, etc.
    
    # Sample result - replace with your actual processing logic
    result = {
        "tickers": tickers,
        "result": {
            "metrics": {
                "sharpeRatio": 1.4,
                "maxDrawdown": 0.12,
                "annualReturn": 0.09
            },
            "statistics": {
                "winRate": 0.58,
                "tradeCount": 320
            },
            "tickerResults": {
                ticker: {
                    "return": 0.1 + (i * 0.02),
                    "volatility": 0.2 - (i * 0.01)
                } for i, ticker in enumerate(tickers)
            }
        }
    }
    
    logger.info(f"Completed processing for tickers: {tickers}")
    
    return result
