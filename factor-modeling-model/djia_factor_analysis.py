import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
from datetime import datetime, timedelta
import os
import sys
import time
import traceback
from clickhouse_driver import Client
import traceback

# DJIA 30 stock tickers
# DJIA_TICKERS = [
#     'AAPL', 'AMGN', 'AMZN', 'AXP', 'BA', 'CAT', 'CRM', 'CSCO', 'CVX', 'DIS',
#     'GS', 'HD', 'HON', 'IBM', 'JNJ', 'JPM', 'KO', 'MCD', 'MMM', 'MRK',
#     'MSFT', 'NKE', 'NVDA', 'PG', 'SHW', 'TRV', 'UNH', 'V', 'VZ', 'WMT'
# ]
# Use DJIA 6 stock tickers as DEV
DJIA_TICKERS = [
    'AAPL', 'AMGN', 'AMZN', 'AXP', 'BA', 'CAT'
]

class ClickHouseDataFetcher:
    """Class to fetch data from ClickHouse database"""
    
    def __init__(self, host='44.222.122.134', port=9000, user='jacky_user', password='your_secure_password', database='jacky_database1'):
        """Initialize the ClickHouse client"""
        self.client = Client(host=host, port=port, user=user, password=password, database=database)
        self.database = database
        
    def fetch_stock_data(self, symbols, start_date, end_date):
        """Fetch stock price data for a list of symbols"""
        print(f"Fetching stock data for {len(symbols)} symbols from {start_date} to {end_date}...")
        
        # Convert dates to ClickHouse format
        start_date_formatted = f"toDateTime('{start_date} 00:00:00')"
        end_date_formatted = f"toDateTime('{end_date} 23:59:59')"
        
        result = {}
        
        for symbol in symbols:
            try:
                # Query to get daily OHLCV data
                query = f"""
                SELECT 
                    symbol,
                    toDate(timestamp) as date,
                    argMin(open, timestamp) as open,
                    max(high) as high,
                    min(low) as low,
                    argMax(close, timestamp) as close,
                    sum(volume) as volume,
                    argMax(adjusted_close, timestamp) as adjusted_close
                FROM {self.database}.tick_data
                WHERE symbol = '{symbol}'
                AND timestamp BETWEEN {start_date_formatted} AND {end_date_formatted}
                GROUP BY symbol, toDate(timestamp)
                ORDER BY date
                """
                
                # Execute query
                data = self.client.execute(query, with_column_types=True)
                
                # Convert to DataFrame
                columns = [col[0] for col in data[1]]
                df = pd.DataFrame(data[0], columns=columns)
                
                # Convert date to datetime
                df['date'] = pd.to_datetime(df['date'])
                
                # Set date as index
                df.set_index('date', inplace=True)
                
                # Store in result dictionary
                result[symbol] = df
                
                print(f"Fetched {len(df)} days of data for {symbol}")
                
                # Add a small delay to avoid overwhelming the server
                time.sleep(0.1)
                
            except Exception as e:
                print(traceback.format_exc())
                print(f"Error fetching data for {symbol}: {str(e)}")
        
        return result
    
    def generate_fundamental_data(self, symbols, price_data):
        """Generate mock fundamental data based on price data"""
        print("Generating fundamental data...")
        
        # Get the union of all dates from price data
        all_dates = set()
        for symbol in symbols:
            if symbol in price_data:
                all_dates.update(price_data[symbol].index)
        
        all_dates = sorted(list(all_dates))
        pe_df = pd.DataFrame(index=all_dates)
        growth_df = pd.DataFrame(index=all_dates)
        
        # Generate data for each stock
        for symbol in symbols:
            if symbol in price_data:
                # Generate P/E ratios (varying over time but related to price)
                prices = price_data[symbol]['adjusted_close']
                
                # Base P/E on price with some randomness
                base_pe = np.random.uniform(10, 30)
                pe_volatility = np.random.uniform(0.005, 0.015)
                pe_changes = np.random.normal(0, pe_volatility, len(prices))
                pe_series = base_pe * (1 + pe_changes).cumprod()
                pe_series = np.clip(pe_series, 5, 100)  # Keep P/E ratios in reasonable range
                pe_df[symbol] = pe_series
                
                # Generate growth rates (varying over time)
                base_growth = np.random.uniform(0.05, 0.25)
                growth_volatility = np.random.uniform(0.002, 0.01)
                growth_changes = np.random.normal(0, growth_volatility, len(prices))
                growth_series = base_growth * (1 + growth_changes).cumprod()
                growth_series = np.clip(growth_series, 0.01, 0.5)
                growth_df[symbol] = growth_series
        
        return pe_df, growth_df
    
    def generate_market_cap_data(self, symbols, price_data):
        """Generate market cap data based on price data"""
        print("Generating market cap data...")
        
        # Get the union of all dates from price data
        all_dates = set()
        for symbol in symbols:
            if symbol in price_data:
                all_dates.update(price_data[symbol].index)
        
        all_dates = sorted(list(all_dates))
        market_cap_df = pd.DataFrame(index=all_dates)
        
        # Generate market cap for each stock
        for symbol in symbols:
            if symbol in price_data:
                # Generate random shares outstanding (between 1B and 10B)
                shares_outstanding = np.random.uniform(1e9, 10e9)
                
                # Calculate market cap as price * shares outstanding
                market_cap = price_data[symbol]['adjusted_close'] * shares_outstanding
                
                # Add to DataFrame
                market_cap_df[symbol] = market_cap
        
        return market_cap_df
    
    def store_factor_results(self, factor_name, results_dict, description=""):
        """
        Store factor test results in ClickHouse
        
        Parameters:
        - factor_name: Name of the factor
        - results_dict: Dictionary containing test results
        - description: Optional description of the factor
        
        Returns:
        - factor_name
        """
        try:
            print(f"Storing {factor_name} factor results in ClickHouse...")
            
            # Extract data from results_dict
            factor_test_results = results_dict.get('factor_test_results', pd.DataFrame())
            performance_results = results_dict.get('performance_results', pd.DataFrame())
            portfolio_returns = results_dict.get('portfolio_returns', pd.DataFrame())
            
            # Create factor_summary table if it doesn't exist
            self.client.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.database}.factor_summary (
                factor_name String,
                test_date Date,
                start_date Date,
                end_date Date,
                avg_beta Float64,
                avg_tstat Float64,
                avg_rsquared Float64,
                significant_stocks Int32,
                total_stocks Int32,
                annualized_return Float64,
                annualized_volatility Float64,
                sharpe_ratio Float64,
                max_drawdown Float64,
                description String,
                update_time DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (factor_name, test_date)
            """)
            
            # Create factor_details table if it doesn't exist
            self.client.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.database}.factor_details (
                factor_name String,
                ticker String,
                beta Float64,
                tstat Float64,
                pvalue Float64,
                rsquared Float64,
                conf_int_lower Float64,
                conf_int_upper Float64,
                update_time DateTime DEFAULT now(),
            ) ENGINE = MergeTree()
            ORDER BY (factor_name, ticker)
            """)
            
            # Create factor_timeseries table if it doesn't exist
            self.client.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.database}.factor_timeseries (
                factor_name String,
                date Date,
                factor_value Float64,
                high_portfolio_return Float64,
                low_portfolio_return Float64,
                update_time DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (factor_name, date)
            """)

            # Prepare summary data
            test_date = datetime.now().date()

            # Get date range from portfolio returns
            if not portfolio_returns.empty:
                start_date = portfolio_returns.index[0]
                end_date = portfolio_returns.index[-1]
            else:
                start_date = datetime.strptime("2000-01-01", '%Y-%m-%d').date()
                end_date = datetime.strptime("2025-03-31", '%Y-%m-%d').date()
            
            # Calculate summary statistics
            avg_beta = float(factor_test_results['Beta'].mean()) if 'Beta' in factor_test_results else 0.0
            avg_tstat = float(factor_test_results['T-stat'].mean()) if 'T-stat' in factor_test_results else 0.0
            avg_rsquared = float(factor_test_results['R-squared'].mean()) if 'R-squared' in factor_test_results else 0.0
            
            significant_stocks = int((abs(factor_test_results['T-stat']) > 1.96).sum()) if 'T-stat' in factor_test_results else 0
            total_stocks = len(factor_test_results) if not factor_test_results.empty else 0
            
            # Get performance metrics
            factor_col = f'{factor_name}_Factor'
            if not performance_results.empty and 'Annualized Return' in performance_results and factor_col in performance_results['Annualized Return']:
                ann_return = float(performance_results['Annualized Return'][factor_col])
                ann_vol = float(performance_results['Annualized Volatility'][factor_col])
                sharpe = float(performance_results['Sharpe Ratio'][factor_col])
                max_dd = float(performance_results['Maximum Drawdown'][factor_col])
            else:
                ann_return = 0.0
                ann_vol = 0.0
                sharpe = 0.0
                max_dd = 0.0
            
            # Insert summary into database
            self.client.execute(f"""
            INSERT INTO {self.database}.factor_summary 
            (factor_name, test_date, start_date, end_date, avg_beta, avg_tstat, avg_rsquared, 
             significant_stocks, total_stocks, annualized_return, annualized_volatility, 
             sharpe_ratio, max_drawdown, description)
            VALUES
            """, [(
                factor_name, test_date, start_date, end_date, avg_beta, avg_tstat, avg_rsquared,
                significant_stocks, total_stocks, ann_return, ann_vol, sharpe, max_dd, 
                description or f"{factor_name} factor analysis results"
            )])
            
            # Store detailed factor test results
            if not factor_test_results.empty:
                details_data = []
                for ticker, row in factor_test_results.iterrows():
                    beta = float(row.get('Beta', 0.0))
                    tstat = float(row.get('T-stat', 0.0))
                    pvalue = float(row.get('P-value', 0.0))
                    rsquared = float(row.get('R-squared', 0.0))
                    conf_int_lower = float(row.get('Conf_Int_Lower', 0.0))
                    conf_int_upper = float(row.get('Conf_Int_Upper', 0.0))
                    
                    details_data.append((
                        factor_name, ticker, beta, tstat, pvalue, rsquared, conf_int_lower, conf_int_upper
                    ))
                
                if details_data:
                    self.client.execute(f"""
                    INSERT INTO {self.database}.factor_details 
                    (factor_name, ticker, beta, tstat, pvalue, rsquared, conf_int_lower, conf_int_upper)
                    VALUES
                    """, details_data)
            
            # Store time series data
            if not portfolio_returns.empty and factor_col in portfolio_returns.columns:
                timeseries_data = []
                for date, row in portfolio_returns.iterrows():
                    factor_value = float(row.get(factor_col, 0.0))
                    high_return = float(row.get(f'High_{factor_name}', 0.0))
                    low_return = float(row.get(f'Low_{factor_name}', 0.0))
                    
                    timeseries_data.append((
                        factor_name, date, factor_value, high_return, low_return
                    ))
                
                if timeseries_data:
                    self.client.execute(f"""
                    INSERT INTO {self.database}.factor_timeseries 
                    (factor_name, date, factor_value, high_portfolio_return, low_portfolio_return)
                    VALUES
                    """, timeseries_data)
            
            print(f"Successfully stored {factor_name} factor results")
            return factor_name
            
        except Exception as e:
            print(f"Error storing factor results: {str(e)}")
            print(traceback.format_exc())
            return None

def calculate_peg(pe_df, growth_df):
    """Calculate PEG ratio from P/E and growth data"""
    peg_df = pd.DataFrame(index=pe_df.index)
    
    for ticker in pe_df.columns:
        if ticker in growth_df.columns:
            # PEG = P/E / Growth rate
            peg_df[ticker] = pe_df[ticker] / (growth_df[ticker] * 100)  # Convert growth to percentage
    
    return peg_df

def calculate_returns(price_data):
    """Calculate daily returns from price data"""
    returns_df = pd.DataFrame()
    
    for symbol, df in price_data.items():
        if 'adjusted_close' in df.columns:
            returns_df[symbol] = df['adjusted_close'].pct_change().fillna(0)
    
    return returns_df

def construct_portfolios(factor_df, returns_df, market_cap_df, factor_name, n_groups=3):
    """Construct portfolios based on factor values"""
    portfolio_returns = pd.DataFrame(index=returns_df.index)
    
    for date in returns_df.index:
        if date not in factor_df.index or date == returns_df.index[0]:
            continue
        
        # Get factor values for previous day to avoid look-ahead bias
        prev_dates = factor_df.index[factor_df.index < date]
        if len(prev_dates) == 0:
            continue
            
        prev_date = prev_dates[-1]
        factor_values = factor_df.loc[prev_date].dropna()
        
        if len(factor_values) < n_groups:
            continue
            
        # Sort stocks by factor
        sorted_stocks = factor_values.sort_values(ascending=False)
        
        # Divide into groups
        group_size = len(sorted_stocks) // n_groups
        
        # High factor group (top half)
        high_factor_stocks = sorted_stocks.iloc[:group_size].index.tolist()
        
        # Low factor group (bottom half)
        low_factor_stocks = sorted_stocks.iloc[-group_size:].index.tolist()
        
        # Calculate market cap weights for each group
        if prev_date in market_cap_df.index:
            high_group_mcap = market_cap_df.loc[prev_date, high_factor_stocks].dropna()
            if not high_group_mcap.empty:
                high_weights = high_group_mcap / high_group_mcap.sum()
            else:
                high_weights = pd.Series(1.0/len(high_factor_stocks), index=high_factor_stocks)
            
            low_group_mcap = market_cap_df.loc[prev_date, low_factor_stocks].dropna()
            if not low_group_mcap.empty:
                low_weights = low_group_mcap / low_group_mcap.sum()
            else:
                low_weights = pd.Series(1.0/len(low_factor_stocks), index=low_factor_stocks)
        else:
            # Equal weights if market cap not available
            high_weights = pd.Series(1.0/len(high_factor_stocks), index=high_factor_stocks)
            low_weights = pd.Series(1.0/len(low_factor_stocks), index=low_factor_stocks)
        
        # Calculate weighted returns for each group
        high_factor_return = (returns_df.loc[date, high_factor_stocks] * high_weights).sum()
        low_factor_return = (returns_df.loc[date, low_factor_stocks] * low_weights).sum()
        
        # Store portfolio returns
        portfolio_returns.loc[date, f'High_{factor_name}'] = high_factor_return
        portfolio_returns.loc[date, f'Low_{factor_name}'] = low_factor_return
        portfolio_returns.loc[date, f'{factor_name}_Factor'] = high_factor_return - low_factor_return
    
    return portfolio_returns.fillna(0)

def test_factor(returns_df, factor_returns):
    """Test factor effectiveness using regression analysis"""
    results = {}
    
    # For each stock, run regression against the factor
    for ticker in returns_df.columns:
        stock_returns = returns_df[ticker].dropna()
        aligned_factor = factor_returns.loc[stock_returns.index].dropna()
        
        # Skip if not enough data
        if len(aligned_factor) < 30:
            continue
            
        # Add constant for intercept
        X = sm.add_constant(aligned_factor)
        
        # Run regression
        model = sm.OLS(stock_returns.loc[aligned_factor.index], X).fit()
        
        # Store results
        results[ticker] = {
            'Alpha': model.params.iloc[0] if len(model.params) > 0 else np.nan,
            'Beta': model.params.iloc[1] if len(model.params) > 1 else np.nan,
            'T-stat': model.tvalues.iloc[1] if len(model.tvalues) > 1 else np.nan,
            'P-value': model.pvalues.iloc[1] if len(model.pvalues) > 1 else np.nan,
            'R-squared': model.rsquared,
            'Conf_Int_Lower': model.conf_int().iloc[1, 0] if len(model.conf_int()) > 1 else np.nan,
            'Conf_Int_Upper': model.conf_int().iloc[1, 1] if len(model.conf_int()) > 1 else np.nan
        }
    
    return pd.DataFrame(results).T

def evaluate_portfolio(portfolio_returns):
    """Evaluate portfolio performance metrics"""
    # Calculate cumulative returns
    cumulative_returns = (1 + portfolio_returns).cumprod()
    
    # Calculate annualized return
    total_days = len(portfolio_returns)
    trading_days_per_year = 252
    years = total_days / trading_days_per_year
    
    annualized_return = {}
    for col in portfolio_returns.columns:
        if cumulative_returns[col].iloc[-1] > 0:
            annualized_return[col] = (cumulative_returns[col].iloc[-1] ** (1/years)) - 1
        else:
            annualized_return[col] = -1  # Handle negative cumulative returns
    
    # Calculate volatility (annualized)
    volatility = {col: portfolio_returns[col].std() * np.sqrt(trading_days_per_year) for col in portfolio_returns.columns}
    
    # Calculate Sharpe ratio (assuming risk-free rate of 0.02)
    risk_free_rate = 0.02
    sharpe_ratio = {
        col: (annualized_return[col] - risk_free_rate) / volatility[col] if volatility[col] > 0 else 0
        for col in portfolio_returns.columns
    }
    
    # Calculate maximum drawdown
    max_drawdown = {}
    for col in portfolio_returns.columns:
        cum_returns = cumulative_returns[col]
        running_max = cum_returns.cummax()
        drawdown = (cum_returns / running_max) - 1
        max_drawdown[col] = drawdown.min()
    
    # Compile results
    results = pd.DataFrame({
        'Annualized Return': annualized_return,
        'Annualized Volatility': volatility,
        'Sharpe Ratio': sharpe_ratio,
        'Maximum Drawdown': max_drawdown
    })
    
    return results, cumulative_returns

def run_peg_factor_analysis(start_date='2025-01-01', end_date='2025-03-31'):
    """Run PEG factor analysis using real data from ClickHouse"""
    try:
        print(f"Running PEG factor analysis from {start_date} to {end_date}...")
        
        # Create data fetcher
        data_fetcher = ClickHouseDataFetcher()
        
        # Fetch stock price data
        price_data = data_fetcher.fetch_stock_data(DJIA_TICKERS, start_date, end_date)
        
        # Generate fundamental data (since we don't have real P/E and growth data)
        pe_df, growth_df = data_fetcher.generate_fundamental_data(DJIA_TICKERS, price_data)
        
        # Generate market cap data
        market_cap_df = data_fetcher.generate_market_cap_data(DJIA_TICKERS, price_data)
        
        # Calculate PEG ratios
        print("Calculating PEG ratios...")
        peg_df = calculate_peg(pe_df, growth_df)
        
        # Calculate daily returns
        print("Calculating daily returns...")
        returns_df = calculate_returns(price_data)
        
        # Construct portfolios
        print("Constructing high and low PEG portfolios...")
        portfolio_returns = construct_portfolios(peg_df, returns_df, market_cap_df, "PEG")
        
        # Test factor effectiveness
        print("Testing PEG factor effectiveness...")
        factor_test_results = test_factor(returns_df, portfolio_returns['PEG_Factor'])
        
        # Evaluate portfolio performance
        print("Evaluating portfolio performance...")
        performance_results, cumulative_returns = evaluate_portfolio(portfolio_returns)
        

        # Print results
        print("\n--- PEG Factor Test Results ---")
        print("\nAverage Factor Test Statistics:")
        print(f"Average Beta: {factor_test_results['Beta'].mean():.4f}")
        print(f"Average T-stat: {factor_test_results['T-stat'].mean():.4f}")
        print(f"Average R-squared: {factor_test_results['R-squared'].mean():.4f}")
        print(f"Significant stocks (|T-stat| > 1.96): {(abs(factor_test_results['T-stat']) > 1.96).sum()} out of {len(factor_test_results)}")
        
        print("\n--- Portfolio Performance ---")
        print(performance_results)
        
        # Plot cumulative returns
        plt.figure(figsize=(12, 6))
        cumulative_returns.plot()
        plt.title('Cumulative Returns of PEG Factor Portfolios')
        plt.xlabel('Date')
        plt.ylabel('Cumulative Return')
        plt.grid(True)
        plt.savefig('peg_factor_cumulative_returns_real_data.png')
        
        # Plot factor test results distribution
        plt.figure(figsize=(15, 10))
        
        plt.subplot(2, 2, 1)
        sns.histplot(factor_test_results['Beta'], kde=True)
        plt.title('Distribution of Beta Coefficients')
        plt.axvline(x=0, color='r', linestyle='--')
        
        plt.subplot(2, 2, 2)
        sns.histplot(factor_test_results['T-stat'], kde=True)
        plt.title('Distribution of T-statistics')
        plt.axvline(x=1.96, color='r', linestyle='--')
        plt.axvline(x=-1.96, color='r', linestyle='--')
        
        plt.subplot(2, 2, 3)
        sns.histplot(factor_test_results['R-squared'], kde=True)
        plt.title('Distribution of R-squared Values')
        
        plt.subplot(2, 2, 4)
        rolling_factor = portfolio_returns['PEG_Factor'].rolling(window=252).mean()
        rolling_factor.plot()
        plt.title('252-Day Rolling Average of PEG Factor Returns')
        plt.axhline(y=0, color='r', linestyle='--')
        
        plt.tight_layout()
        plt.savefig('peg_factor_statistics_real_data.png')
        
        # Return results for further analysis
        return {
            'prices': price_data,
            'pe_ratios': pe_df,
            'growth_rates': growth_df,
            'peg_ratios': peg_df,
            'returns': returns_df,
            'portfolio_returns': portfolio_returns,
            'factor_test_results': factor_test_results,
            'performance_results': performance_results
        }
        
    except Exception as e:
        print(f"Error in PEG factor analysis: {str(e)}")
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    # Run PEG factor analysis
    results = run_peg_factor_analysis()
    
    # Save results to CSV files
    if results:
        os.makedirs('factor_results', exist_ok=True)
        
        # Save factor test results
        results['factor_test_results'].to_csv('factor_results/peg_factor_test_results.csv')
        
        # Save performance results
        results['performance_results'].to_csv('factor_results/peg_performance_results.csv')
        
        # Save portfolio returns
        results['portfolio_returns'].to_csv('factor_results/peg_portfolio_returns.csv')
        
        print("\nAnalysis complete. Results saved to 'factor_results' directory.")
    def close(self):
        """Close the client connection"""
        self.client.disconnect()
