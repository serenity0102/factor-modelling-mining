import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Split a date range into individual years.
    
    Input:
    {
        "startYear": 2000,
        "endYear": 2010
    }
    
    Output:
    [2000, 2001, 2002, ..., 2010]
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    start_year = int(event.get('startYear'))
    end_year = int(event.get('endYear'))
    
    if start_year > end_year:
        raise ValueError(f"Start year {start_year} is greater than end year {end_year}")
    
    years = list(range(start_year, end_year + 1))
    
    logger.info(f"Generated years: {years}")
    
    return years
