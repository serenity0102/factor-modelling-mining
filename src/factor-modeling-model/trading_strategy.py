import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import backtrader as bt
import os

from clickhouse_utils import ClickHouseUtils
from config import CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_USER, CLICKHOUSE_PASSWORD, CLICKHOUSE_DATABASE
from config import DJIA_TICKERS, START_DATE, END_DATE

class FactorLongShortStrategy:
    """
    Long-Short trading strategy based on multiple factors
    """
    
    def __init__(self, factor_names=None, weights=None):
        """
        Initialize the strategy
        
        Parameters:
        - factor_names: List of factor names to use
        - weights: Dictionary of factor weights (key=factor_name, value=weight)
        """
        self.factor_names = factor_names or [
            "PEG", "RSI14", "RSI28", "SMB", "HML", "Rm_Rf", "PB", "TradingVolume", 
            "ROC20", "CurrentRatio", "CashRatio", "InventoryTurnover", "GrossProfitMargin",
            "DebtToEquity", "InterestCoverage", "RevenueGrowth", "BoardAge", 
            "ExecCompToRevenue", "EnvRating", "AvgSentiment14"
        ]
        
        # Default weights - equal weighting
        if weights is None:
            self.weights = {factor: 1.0 for factor in self.factor_names}
        else:
            self.weights = weights
        
        # Initialize ClickHouse utils
        self.ch_utils = ClickHouseUtils(
            host=CLICKHOUSE_HOST,
            port=CLICKHOUSE_PORT,
            user=CLICKHOUSE_USER,
            password=CLICKHOUSE_PASSWORD,
            database=CLICKHOUSE_DATABASE
        )
    
    def calculate_factor_scores(self, date):
        """
        Calculate factor scores for all stocks on a given date
        
        Parameters:
        - date: Date to calculate scores for
        
        Returns:
        - DataFrame with factor scores for each stock
        """
        # Get factor values for all stocks on the given date
        factor_values = {}
        
        for factor_name in self.factor_names:
            # Query factor values from database
            query = f"""
            SELECT ticker, value
            FROM {CLICKHOUSE_DATABASE}.factor_values
            WHERE factor_name = '{factor_name}'
            AND date = '{date}'
            """
            
            try:
                results = self.ch_utils.client.execute(query)
                if results:
                    factor_values[factor_name] = {ticker: value for ticker, value in results}
            except Exception as e:
                print(f"Error querying factor values for {factor_name}: {e}")
        
        # Create DataFrame with factor values
        df = pd.DataFrame(index=DJIA_TICKERS)
        
        for factor_name, values in factor_values.items():
            df[factor_name] = pd.Series(values)
        
        # Calculate Z-scores for each factor
        z_scores = pd.DataFrame(index=df.index)
        
        for factor_name in factor_values.keys():
            if factor_name in df.columns:
                # Calculate Z-score: (value - mean) / std
                mean = df[factor_name].mean()
                std = df[factor_name].std()
                
                if std > 0:
                    z_scores[factor_name] = (df[factor_name] - mean) / std
                else:
                    z_scores[factor_name] = 0
        
        # Calculate weighted factor score
        factor_score = pd.Series(0, index=z_scores.index)
        
        for factor_name in z_scores.columns:
            if factor_name in self.weights:
                factor_score += z_scores[factor_name] * self.weights[factor_name]
        
        # Normalize the final score
        if len(factor_score) > 0 and factor_score.std() > 0:
            factor_score = (factor_score - factor_score.mean()) / factor_score.std()
        
        return factor_score
    
    def construct_portfolio(self, date, factor_score, market_cap):
        """
        Construct long-short portfolio based on factor scores
        
        Parameters:
        - date: Date to construct portfolio for
        - factor_score: Series with factor scores for each stock
        - market_cap: Series with market cap values for each stock
        
        Returns:
        - Dictionary with long and short positions
        """
        # Sort stocks by factor score
        sorted_stocks = factor_score.sort_values(ascending=False)
        
        # Select top 40% for long positions (12 stocks for DJIA 30)
        long_count = int(len(sorted_stocks) * 0.4)
        long_stocks = sorted_stocks.index[:long_count]
        
        # Select bottom 20% for short positions (6 stocks for DJIA 30)
        short_count = int(len(sorted_stocks) * 0.2)
        short_stocks = sorted_stocks.index[-short_count:]
        
        # Calculate market cap weights
        long_market_cap = market_cap[long_stocks]
        short_market_cap = market_cap[short_stocks]
        
        # Normalize weights to sum to 1
        long_weights = long_market_cap / long_market_cap.sum() if long_market_cap.sum() > 0 else pd.Series(1/len(long_stocks), index=long_stocks)
        short_weights = short_market_cap / short_market_cap.sum() if short_market_cap.sum() > 0 else pd.Series(1/len(short_stocks), index=short_stocks)
        
        # Scale weights by target allocation (80% long, 50% short)
        long_allocation = 0.8
        short_allocation = 0.5
        
        long_positions = long_weights * long_allocation
        short_positions = short_weights * short_allocation * -1  # Negative for short positions
        
        return {
            'long': long_positions,
            'short': short_positions,
            'long_stocks': long_stocks,
            'short_stocks': short_stocks
        }
    
    def get_market_cap(self, date):
        """
        Get market cap for all stocks on a given date
        
        Parameters:
        - date: Date to get market cap for
        
        Returns:
        - Series with market cap values for each stock
        """
        # Query market cap from database or use synthetic data
        # For simplicity, we'll generate synthetic market cap data
        market_cap = pd.Series(index=DJIA_TICKERS)
        
        for ticker in DJIA_TICKERS:
            # Generate random market cap between $10B and $500B
            market_cap[ticker] = np.random.uniform(10e9, 500e9)
        
        return market_cap
    
    def run_strategy(self, start_date, end_date, rebalance_freq='M'):
        """
        Run the trading strategy over a date range
        
        Parameters:
        - start_date: Start date for the strategy
        - end_date: End date for the strategy
        - rebalance_freq: Rebalancing frequency ('D'=daily, 'W'=weekly, 'M'=monthly)
        
        Returns:
        - DataFrame with portfolio positions over time
        """
        # Convert dates to datetime
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        # Generate rebalancing dates
        if rebalance_freq == 'D':
            rebalance_dates = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days
        elif rebalance_freq == 'W':
            rebalance_dates = pd.date_range(start=start_date, end=end_date, freq='W-FRI')  # Weekly on Friday
        else:  # Default to monthly
            rebalance_dates = pd.date_range(start=start_date, end=end_date, freq='BM')  # Business month end
        
        # Filter dates to be within range
        rebalance_dates = rebalance_dates[(rebalance_dates >= start_date) & (rebalance_dates <= end_date)]
        
        # Initialize portfolio positions DataFrame
        positions = pd.DataFrame(index=rebalance_dates, columns=DJIA_TICKERS)
        positions = positions.fillna(0)
        
        # Track portfolio composition
        portfolio_composition = {
            'dates': [],
            'long_stocks': [],
            'short_stocks': []
        }
        
        # Run strategy for each rebalancing date
        for date in rebalance_dates:
            date_str = date.strftime('%Y-%m-%d')
            print(f"Rebalancing portfolio on {date_str}")
            
            try:
                # Calculate factor scores
                factor_score = self.calculate_factor_scores(date_str)
                
                # Get market cap
                market_cap = self.get_market_cap(date_str)
                
                # Construct portfolio
                portfolio = self.construct_portfolio(date_str, factor_score, market_cap)
                
                # Update positions
                for ticker, weight in portfolio['long'].items():
                    positions.loc[date, ticker] = weight
                
                for ticker, weight in portfolio['short'].items():
                    positions.loc[date, ticker] = weight
                
                # Track portfolio composition
                portfolio_composition['dates'].append(date_str)
                portfolio_composition['long_stocks'].append(list(portfolio['long_stocks']))
                portfolio_composition['short_stocks'].append(list(portfolio['short_stocks']))
                
            except Exception as e:
                print(f"Error on {date_str}: {e}")
        
        return positions, portfolio_composition
