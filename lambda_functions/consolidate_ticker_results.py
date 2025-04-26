import json
import logging
from statistics import mean

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Consolidate results from individual ticker processing.
    
    Input:
    {
        "tickerResults": [
            {
                "ticker": "AAPL",
                "result": {...}
            },
            {
                "ticker": "MSFT",
                "result": {...}
            },
            ...
        ]
    }
    
    Output:
    {
        "summary": {
            "averageMetrics": {...},
            "tickerResults": [...]
        }
    }
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    ticker_results = event.get('tickerResults', [])
    
    if not ticker_results:
        return {
            "summary": {
                "averageMetrics": {},
                "tickerResults": []
            }
        }
    
    # Extract metrics for averaging
    returns = []
    volatilities = []
    sharpe_ratios = []
    max_drawdowns = []
    win_rates = []
    
    # Create a dictionary of ticker results for easy lookup
    ticker_dict = {}
    
    for result in ticker_results:
        if 'result' in result:
            ticker = result.get('ticker')
            ticker_dict[ticker] = result
            
            metrics = result['result']
            returns.append(metrics.get('return', 0))
            volatilities.append(metrics.get('volatility', 0))
            sharpe_ratios.append(metrics.get('sharpeRatio', 0))
            max_drawdowns.append(metrics.get('maxDrawdown', 0))
            win_rates.append(metrics.get('winRate', 0))
    
    # Calculate averages
    avg_metrics = {
        "averageReturn": mean(returns) if returns else 0,
        "averageVolatility": mean(volatilities) if volatilities else 0,
        "averageSharpeRatio": mean(sharpe_ratios) if sharpe_ratios else 0,
        "averageMaxDrawdown": mean(max_drawdowns) if max_drawdowns else 0,
        "averageWinRate": mean(win_rates) if win_rates else 0,
        "totalTickers": len(ticker_results)
    }
    
    # Create summary
    summary = {
        "averageMetrics": avg_metrics,
        "tickerResults": ticker_results
    }
    
    logger.info("Consolidation complete")
    
    return {
        "summary": summary
    }
