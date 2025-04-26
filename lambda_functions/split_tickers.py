import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Split a list of tickers into individual ticker items.
    
    Input:
    {
        "tickers": ["AAPL", "MSFT", "GOOG", "AMZN", "META"],
        "additionalParams": {
            "param1": "value1",
            "param2": "value2"
        }
    }
    
    Output:
    [
        {"ticker": "AAPL", "additionalParams": {...}},
        {"ticker": "MSFT", "additionalParams": {...}},
        ...
    ]
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    tickers = event.get('tickers', [])
    additional_params = event.get('additionalParams', {})
    
    logger.info(f"Splitting tickers: {tickers}")
    
    # Create a list of individual ticker objects
    ticker_items = []
    for ticker in tickers:
        ticker_items.append({
            "ticker": ticker,
            "additionalParams": additional_params
        })
    
    logger.info(f"Generated {len(ticker_items)} ticker items")
    
    return ticker_items
