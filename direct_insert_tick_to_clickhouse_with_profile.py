import yfinance as yf
import clickhouse_driver
import pandas as pd
from datetime import datetime
import boto3
import json
import os

def get_secret(secret_name, region_name="us-east-1", profile_name="kenchowt+eks-auto-Admin"):
    """
    Retrieve a secret from AWS Secrets Manager using a specific AWS profile
    
    Parameters:
    -----------
    secret_name : str
        Name of the secret in AWS Secrets Manager
    region_name : str
        AWS region where the secret is stored
    profile_name : str
        AWS profile name to use
        
    Returns:
    --------
    dict
        Dictionary containing the secret key/value pairs
    """
    # Create a Secrets Manager client using the specified profile
    session = boto3.session.Session(profile_name=profile_name)
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        raise e
    else:
        # Depending on whether the secret is a string or binary, one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return json.loads(secret)
        else:
            # If the secret is binary, we'll need to decode it
            import base64
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return json.loads(decoded_binary_secret)

def download_and_insert_tick_data(ticker, start_date, end_date, host, secret_name, region_name="us-east-1", profile_name="kenchowt+eks-auto-Admin", port=9000, database='tick_data_database_2'):
    """
    Download tick data from Yahoo Finance and insert directly into ClickHouse
    
    Parameters:
    -----------
    ticker : str
        Stock ticker symbol (e.g., 'BA')
    start_date : str
        Start date in 'YYYY-MM-DD' format
    end_date : str
        End date in 'YYYY-MM-DD' format
    host : str
        ClickHouse server hostname or IP
    secret_name : str
        Name of the secret in AWS Secrets Manager containing DB credentials
    region_name : str
        AWS region where the secret is stored
    profile_name : str
        AWS profile name to use
    port : int
        ClickHouse server port
    database : str
        ClickHouse database name
    """
    print(f"Downloading data for {ticker} from {start_date} to {end_date}...")
    
    # Download data from Yahoo Finance
    data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)
    
    if data.empty:
        print(f"No data found for {ticker} in the specified date range.")
        return
    
    print(f"Downloaded {len(data)} rows of data.")
    
    # Reset index to make Date a column
    data.reset_index(inplace=True)
    
    # Print the first few rows to understand the structure
    print("Data sample:")
    print(data.head())
    
    try:
        # Get database credentials from Secrets Manager using the specified profile
        secret = get_secret(secret_name, region_name, profile_name)
        user = secret.get('username', 'default')
        password = secret.get('password', '')
        
        # Connect to ClickHouse
        client = clickhouse_driver.Client(
            host=host,
            port=port,
            user=user,
            password=password
        )
        
        # Create database if it doesn't exist
        client.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        print(f"Database '{database}' created or already exists.")
        
        # Create table if it doesn't exist
        create_table_query = f'''
        CREATE TABLE IF NOT EXISTS {database}.tick_data
        (
            symbol String,
            timestamp DateTime,
            open Float64,
            high Float64,
            low Float64,
            close Float64,
            volume UInt64,
            adjusted_close Float64
        )
        ENGINE = MergeTree()
        ORDER BY (symbol, timestamp)
        '''
        
        client.execute(create_table_query)
        print(f"Table '{database}.tick_data' created or already exists.")
        
        # Get existing timestamps for this ticker
        existing_timestamps = client.execute(
            f"SELECT timestamp FROM {database}.tick_data WHERE symbol = %(symbol)s",
            {'symbol': ticker}
        )
        existing_timestamps = [ts[0] for ts in existing_timestamps]
        
        # Save to CSV first to simplify data handling
        temp_csv = f"{ticker}_temp.csv"
        data.to_csv(temp_csv, index=False)
        print(f"Saved data to temporary CSV: {temp_csv}")
        
        # Read back the CSV to get clean data
        clean_data = pd.read_csv(temp_csv)
        
        # Convert data to a list of tuples for insertion
        rows = []
        for _, row in clean_data.iterrows():
            # Skip header row if it exists
            if pd.isna(row['Date']) or not isinstance(row['Date'], str):
                continue
                
            try:
                # Convert string date to datetime
                date_obj = datetime.strptime(row['Date'], '%Y-%m-%d')
                
                # Skip if timestamp already exists
                if date_obj in existing_timestamps:
                    continue
                
                # Extract values
                open_val = float(row['Open'])
                high_val = float(row['High'])
                low_val = float(row['Low'])
                close_val = float(row['Close'])
                volume_val = int(row['Volume'])
                adj_close_val = float(row['Adj Close'])
                
                rows.append((
                    ticker,
                    date_obj,
                    open_val,
                    high_val,
                    low_val,
                    close_val,
                    volume_val,
                    adj_close_val
                ))
            except (ValueError, TypeError) as e:
                print(f"Skipping row due to error: {e}")
                print(f"Problematic row: {row}")
                continue
        
        # Insert data into ClickHouse
        if rows:
            client.execute(
                f'INSERT INTO {database}.tick_data (symbol, timestamp, open, high, low, close, volume, adjusted_close) VALUES',
                rows
            )
            
            print(f"Successfully inserted {len(rows)} new rows for {ticker} into ClickHouse.")
            
            # Verify data was inserted
            count = client.execute(f"SELECT COUNT(*) FROM {database}.tick_data WHERE symbol = '{ticker}'")
            print(f"Total rows for {ticker} in database: {count[0][0]}")
            
            # Clean up temporary CSV file
            os.remove(temp_csv)
            print(f"Removed temporary CSV file: {temp_csv}")
        else:
            print("No new rows to insert")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Configuration
    # DOW30 stocks as of April 2025
    DOW30_TICKERS = [
    'AAPL', 'AMGN', 'AMZN', 'AXP', 'BA', 'CAT', 'CRM', 'CSCO', 'CVX', 'DIS', 'GS', 'HD', 'HON', 'IBM', 'JNJ', 'JPM', 'KO', 'MCD', 'MMM', 'MRK', 'MSFT', 'NKE', 'NVDA', 'PG', 'SHW', 'TRV', 'UNH', 'V', 'VZ', 'WMT'
    ]
    START_DATE = "2000-01-01"
    END_DATE = datetime.today().strftime('%Y-%m-%d')
    SECRET_NAME = "clickhouse/password"  # Secret name in AWS Secrets Manager
    REGION_NAME = "us-east-1"  # AWS region where your secret is stored
    PROFILE_NAME = "kenchowt+eks-auto-Admin"  # AWS profile name to use
    CLICKHOUSE_HOST = "44.222.122.134"  # ClickHouse server hostname or IP
    
    # Process each DOW30 stock
    for ticker in DOW30_TICKERS:
        print(f"\n{'='*50}")
        print(f"Processing {ticker}...")
        print(f"{'='*50}")
        try:
            # Execute the function for each ticker
            download_and_insert_tick_data(
                ticker=ticker,
                start_date=START_DATE,
                end_date=END_DATE,
                host=CLICKHOUSE_HOST,
                secret_name=SECRET_NAME,
                region_name=REGION_NAME,
                profile_name=PROFILE_NAME
            )
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            # Continue with the next ticker even if one fails
            continue
        
    print("\nCompleted processing all DOW30 stocks.")
