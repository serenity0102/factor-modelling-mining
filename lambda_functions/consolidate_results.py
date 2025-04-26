import json
import logging
from statistics import mean

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Consolidate results from individual year processing.
    
    Input:
    {
        "yearResults": [
            {
                "year": 2000,
                "result": {...}
            },
            {
                "year": 2001,
                "result": {...}
            },
            ...
        ]
    }
    
    Output:
    {
        "summary": {
            "averageMetrics": {...},
            "yearlyResults": [...]
        }
    }
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    year_results = event.get('yearResults', [])
    
    if not year_results:
        return {
            "summary": {
                "averageMetrics": {},
                "yearlyResults": []
            }
        }
    
    # Sort results by year
    year_results.sort(key=lambda x: x.get('year', 0))
    
    # Extract metrics for averaging
    sharpe_ratios = [yr['result']['metrics']['sharpeRatio'] for yr in year_results if 'result' in yr]
    max_drawdowns = [yr['result']['metrics']['maxDrawdown'] for yr in year_results if 'result' in yr]
    annual_returns = [yr['result']['metrics']['annualReturn'] for yr in year_results if 'result' in yr]
    win_rates = [yr['result']['statistics']['winRate'] for yr in year_results if 'result' in yr]
    
    # Calculate averages
    avg_metrics = {
        "averageSharpeRatio": mean(sharpe_ratios) if sharpe_ratios else 0,
        "averageMaxDrawdown": mean(max_drawdowns) if max_drawdowns else 0,
        "averageAnnualReturn": mean(annual_returns) if annual_returns else 0,
        "averageWinRate": mean(win_rates) if win_rates else 0,
        "totalYears": len(year_results)
    }
    
    # Create summary
    summary = {
        "averageMetrics": avg_metrics,
        "yearlyResults": year_results
    }
    
    logger.info("Consolidation complete")
    
    return {
        "summary": summary
    }
