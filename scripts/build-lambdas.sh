#!/bin/bash

# Script to build Lambda function packages

# Create directory for Lambda packages
mkdir -p build

# Build calculate_date_ranges Lambda
echo "Building calculate_date_ranges Lambda..."
cd terraform/modules/step-functions/lambda
mkdir -p calculate_date_ranges
cat > calculate_date_ranges/lambda_function.py << 'EOF'
import os
import datetime
import math

def lambda_handler(event, context):
    # Get the number of date ranges from the event or environment variable
    n = event.get('N', int(os.environ.get('DEFAULT_N', 5)))
    
    # Parse start and end dates
    start_date = datetime.datetime.strptime(event['START_DATE'], '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(event['END_DATE'], '%Y-%m-%d').date()
    
    # Calculate total days and days per period
    total_days = (end_date - start_date).days
    days_per_period = math.ceil(total_days / n)
    
    date_ranges = []
    
    for i in range(n):
        period_start = start_date + datetime.timedelta(days=i * days_per_period)
        period_end = min(period_start + datetime.timedelta(days=days_per_period - 1), end_date)
        
        date_ranges.append({
            'start': period_start.strftime('%Y-%m-%d'),
            'end': period_end.strftime('%Y-%m-%d')
        })
    
    # Return the original event with date ranges added
    return {
        **event,
        'dateRanges': date_ranges
    }
EOF

cd calculate_date_ranges
zip -r ../calculate_date_ranges.zip .
cd ..

# Build calculate_ticker_groups Lambda
echo "Building calculate_ticker_groups Lambda..."
mkdir -p calculate_ticker_groups
cat > calculate_ticker_groups/lambda_function.py << 'EOF'
import os
import math

def lambda_handler(event, context):
    # Get the number of ticker groups from the event or environment variable
    m = event.get('M', int(os.environ.get('DEFAULT_M', 6)))
    
    # Split the tickers string into a list
    tickers = event['DJIA_TICKERS'].split(',')
    
    # Calculate tickers per group
    tickers_per_group = math.ceil(len(tickers) / m)
    
    ticker_groups = []
    
    for i in range(m):
        start_idx = i * tickers_per_group
        end_idx = min(start_idx + tickers_per_group, len(tickers))
        
        if start_idx < len(tickers):
            group = ','.join(tickers[start_idx:end_idx])
            ticker_groups.append(group)
    
    # Return the original event with ticker groups added
    return {
        **event,
        'tickerGroups': ticker_groups
    }
EOF

cd calculate_ticker_groups
zip -r ../calculate_ticker_groups.zip .
cd ..

echo "Lambda packages built successfully!"
