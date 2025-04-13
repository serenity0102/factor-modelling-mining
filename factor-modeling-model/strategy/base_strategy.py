"""
Base Strategy Module

This module defines the base class for all trading strategies.
All specific strategy implementations should inherit from this class.
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
import os
import traceback
from datetime import datetime
import logging

from clickhouse_utils import ClickHouseUtils
from config import CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_USER, CLICKHOUSE_PASSWORD, CLICKHOUSE_DATABASE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BaseStrategy(ABC):
    """
    Base class for all trading strategies.
    
    This abstract class defines the interface that all strategy implementations must follow.
    It provides common functionality for factor calculation, portfolio construction, and backtesting.
    """
    
    def __init__(self, 
                 factor_names=None, 
                 factor_weights=None,
                 tickers=None,
                 start_date=None, 
                 end_date=None,
                 rebalance_freq='M',
                 stop_loss=None,
                 take_profit=None,
                 strategy_id=None):
        """
        Initialize the strategy.
        
        Parameters:
        - factor_names: List of factor names to use
        - factor_weights: Dictionary of factor weights (key=factor_name, value=weight)
        - tickers: List of stock tickers to trade
        - start_date: Start date for the strategy (YYYY-MM-DD)
        - end_date: End date for the strategy (YYYY-MM-DD)
        - rebalance_freq: Rebalancing frequency ('D'=daily, 'W'=weekly, 'M'=monthly)
        - stop_loss: Stop loss percentage (e.g., 0.05 for 5%)
        - take_profit: Take profit percentage (e.g., 0.10 for 10%)
        - strategy_id: Unique identifier for the strategy instance
        """
        # Set strategy parameters
        self.factor_names = factor_names
        self.factor_weights = factor_weights or {}
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.rebalance_freq = rebalance_freq
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.strategy_id = strategy_id or f"{self.__class__.__name__}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Initialize ClickHouse utils
        self.ch_utils = ClickHouseUtils(
            host=CLICKHOUSE_HOST,
            port=CLICKHOUSE_PORT,
            user=CLICKHOUSE_USER,
            password=CLICKHOUSE_PASSWORD,
            database=CLICKHOUSE_DATABASE
        )
        
        # Initialize performance metrics
        self.performance_metrics = {}
        
        logger.info(f"Initialized {self.__class__.__name__} with ID: {self.strategy_id}")
    
    def calculate_factor_scores(self, date):
        """
        Calculate factor scores for all stocks on a given date.
        
        Parameters:
        - date: Date to calculate scores for (YYYY-MM-DD)
        
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
            AND ticker IN ({','.join([f"'{ticker}'" for ticker in self.tickers])})
            """
            
            try:
                results = self.ch_utils.client.execute(query)
                if results:
                    factor_values[factor_name] = {ticker: value for ticker, value in results}
            except Exception as e:
                logger.error(f"Error querying factor values for {factor_name}: {e}")
                print(traceback.format_exc())  # Print full traceback
        
        # Create DataFrame with factor values
        df = pd.DataFrame(index=self.tickers)
        
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
            if factor_name in self.factor_weights:
                weight = self.factor_weights.get(factor_name, 1.0)
                factor_score += z_scores[factor_name] * weight
        
        # Normalize the final score
        if len(factor_score) > 0 and factor_score.std() > 0:
            factor_score = (factor_score - factor_score.mean()) / factor_score.std()
        
        return factor_score
    
    def get_market_cap(self, date):
        """
        Get market cap for all stocks on a given date.
        
        Parameters:
        - date: Date to get market cap for (YYYY-MM-DD)
        
        Returns:
        - Series with market cap values for each stock
        """
        # Query market cap from database
        query = f"""
        SELECT ticker, market_cap
        FROM {CLICKHOUSE_DATABASE}.stock_data
        WHERE date = '{date}'
        AND ticker IN ({','.join([f"'{ticker}'" for ticker in self.tickers])})
        """
        
        try:
            results = self.ch_utils.client.execute(query)
            if results:
                market_cap = pd.Series({ticker: cap for ticker, cap in results}, index=self.tickers)
                return market_cap
        except Exception as e:
            logger.error(f"Error querying market cap: {e}")
            print(traceback.format_exc())  # Print full traceback
        
        # Fallback to synthetic data if database query fails
        logger.warning("Using synthetic market cap data")
        market_cap = pd.Series(index=self.tickers)
        
        for ticker in self.tickers:
            # Generate random market cap between $10B and $500B
            market_cap[ticker] = np.random.uniform(10e9, 500e9)
        
        return market_cap
    
    def get_price_data(self, start_date, end_date):
        """
        Get price data for all stocks in the date range.
        
        Parameters:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        
        Returns:
        - DataFrame with price data for each stock
        """
        # Query price data from database
        query = f"""
        SELECT ticker, date, close
        FROM {CLICKHOUSE_DATABASE}.tick_data
        WHERE date BETWEEN '{start_date}' AND '{end_date}'
        AND ticker IN ({','.join([f"'{ticker}'" for ticker in self.tickers])})
        ORDER BY ticker, date
        """
        
        try:
            results = self.ch_utils.client.execute(query)
            if results:
                # Convert to DataFrame
                df = pd.DataFrame(results, columns=['ticker', 'date', 'close'])
                
                # Pivot to wide format
                price_data = df.pivot(index='date', columns='ticker', values='close')
                return price_data
        except Exception as e:
            logger.error(f"Error querying price data: {e}")
            print(traceback.format_exc())  # Print full traceback
        
        # Fallback to synthetic data if database query fails
        logger.warning("Using synthetic price data")
        
        # Generate dates
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        
        # Initialize price DataFrame
        price_data = pd.DataFrame(index=dates, columns=self.tickers)
        
        # Generate synthetic price data for each ticker
        for ticker in self.tickers:
            np.random.seed(hash(ticker) % 10000)  # Use ticker as seed for reproducibility
            
            # Start price between $50 and $200
            start_price = np.random.uniform(50, 200)
            
            # Generate returns with some autocorrelation
            returns = np.random.normal(0.0005, 0.015, len(dates))  # Mean 5bps daily, 1.5% volatility
            
            # Add autocorrelation
            for i in range(1, len(returns)):
                returns[i] = 0.2 * returns[i-1] + 0.8 * returns[i]
            
            # Calculate prices
            prices = start_price * np.cumprod(1 + returns)
            
            # Add to DataFrame
            price_data[ticker] = prices
        
        return price_data
    
    @abstractmethod
    def construct_portfolio(self, date, factor_score, market_cap):
        """
        Construct portfolio based on factor scores.
        
        Parameters:
        - date: Date to construct portfolio for (YYYY-MM-DD)
        - factor_score: Series with factor scores for each stock
        - market_cap: Series with market cap values for each stock
        
        Returns:
        - Dictionary with portfolio positions
        """
        pass
    
    def run_strategy(self):
        """
        Run the trading strategy over the specified date range.
        
        Returns:
        - DataFrame with portfolio positions over time
        - Dictionary with portfolio composition over time
        """
        # Convert dates to datetime
        start_date = pd.to_datetime(self.start_date)
        end_date = pd.to_datetime(self.end_date)
        
        # Generate rebalancing dates
        if self.rebalance_freq == 'D':
            rebalance_dates = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days
        elif self.rebalance_freq == 'W':
            rebalance_dates = pd.date_range(start=start_date, end=end_date, freq='W-FRI')  # Weekly on Friday
        else:  # Default to monthly
            rebalance_dates = pd.date_range(start=start_date, end=end_date, freq='BM')  # Business month end
        
        # Filter dates to be within range
        rebalance_dates = rebalance_dates[(rebalance_dates >= start_date) & (rebalance_dates <= end_date)]
        
        # Initialize portfolio positions DataFrame
        positions = pd.DataFrame(index=rebalance_dates, columns=self.tickers)
        positions = positions.fillna(0)
        
        # Track portfolio composition
        portfolio_composition = {
            'dates': [],
            'positions': []
        }
        
        # Run strategy for each rebalancing date
        for date in rebalance_dates:
            date_str = date.strftime('%Y-%m-%d')
            logger.info(f"Rebalancing portfolio on {date_str}")
            
            try:
                # Calculate factor scores
                factor_score = self.calculate_factor_scores(date_str)
                
                # Get market cap
                market_cap = self.get_market_cap(date_str)
                
                # Construct portfolio
                portfolio = self.construct_portfolio(date_str, factor_score, market_cap)
                
                # Update positions
                for ticker, weight in portfolio['positions'].items():
                    positions.loc[date, ticker] = weight
                
                # Track portfolio composition
                portfolio_composition['dates'].append(date_str)
                portfolio_composition['positions'].append(portfolio)
                
            except Exception as e:
                logger.error(f"Error on {date_str}: {e}")
                print(traceback.format_exc())  # Print full traceback
        
        return positions, portfolio_composition
    
    def apply_risk_management(self, positions, price_data):
        """
        Apply risk management rules (stop-loss, take-profit) to positions.
        
        Parameters:
        - positions: DataFrame with portfolio positions over time
        - price_data: DataFrame with price data for each stock
        
        Returns:
        - DataFrame with adjusted positions
        """
        if self.stop_loss is None and self.take_profit is None:
            return positions
        
        # Make a copy of positions to avoid modifying the original
        adjusted_positions = positions.copy()
        
        # Get all dates in the price data
        all_dates = price_data.index
        
        # Track active positions and their entry prices
        active_positions = {}
        
        # Process each rebalance date
        for i, rebalance_date in enumerate(positions.index):
            # Get positions on this rebalance date
            current_positions = positions.loc[rebalance_date]
            
            # Update active positions
            for ticker in self.tickers:
                position = current_positions[ticker]
                
                if position != 0:
                    # This is a new or updated position
                    active_positions[ticker] = {
                        'position': position,
                        'entry_price': price_data.loc[rebalance_date, ticker],
                        'entry_date': rebalance_date
                    }
                else:
                    # Position closed
                    if ticker in active_positions:
                        del active_positions[ticker]
            
            # Determine next rebalance date
            next_rebalance_date = positions.index[i+1] if i+1 < len(positions.index) else all_dates[-1]
            
            # Get all dates between current and next rebalance
            date_range = all_dates[(all_dates > rebalance_date) & (all_dates <= next_rebalance_date)]
            
            # Check each date for stop-loss or take-profit triggers
            for date in date_range:
                for ticker, position_info in list(active_positions.items()):
                    position = position_info['position']
                    entry_price = position_info['entry_price']
                    current_price = price_data.loc[date, ticker]
                    
                    # Calculate return
                    price_return = (current_price / entry_price - 1) * np.sign(position)
                    
                    # Check stop-loss
                    if self.stop_loss is not None and price_return < -self.stop_loss:
                        logger.info(f"Stop-loss triggered for {ticker} on {date}")
                        # Close position
                        adjusted_positions.loc[date:next_rebalance_date, ticker] = 0
                        del active_positions[ticker]
                    
                    # Check take-profit
                    elif self.take_profit is not None and price_return > self.take_profit:
                        logger.info(f"Take-profit triggered for {ticker} on {date}")
                        # Close position
                        adjusted_positions.loc[date:next_rebalance_date, ticker] = 0
                        del active_positions[ticker]
        
        return adjusted_positions
    
    def calculate_performance(self, positions, price_data):
        """
        Calculate performance metrics for the strategy.
        
        Parameters:
        - positions: DataFrame with portfolio positions over time
        - price_data: DataFrame with price data for each stock
        
        Returns:
        - Dictionary with performance metrics
        """
        # Calculate daily returns for each stock
        returns = price_data.pct_change().fillna(0)
        
        # Calculate portfolio returns
        portfolio_returns = pd.Series(0.0, index=returns.index)
        
        # Process each rebalance date
        for i, rebalance_date in enumerate(positions.index):
            # Get positions on this rebalance date
            current_positions = positions.loc[rebalance_date]
            
            # Determine next rebalance date
            next_rebalance_date = positions.index[i+1] if i+1 < len(positions.index) else returns.index[-1]
            
            # Get all dates between current and next rebalance
            date_range = returns.index[(returns.index >= rebalance_date) & (returns.index <= next_rebalance_date)]
            
            # Calculate weighted returns for this period
            for date in date_range:
                if date == rebalance_date:
                    continue  # Skip rebalance date (no returns yet)
                
                daily_return = 0
                for ticker in self.tickers:
                    weight = current_positions[ticker]
                    stock_return = returns.loc[date, ticker]
                    daily_return += weight * stock_return
                
                portfolio_returns[date] = daily_return
        
        # Calculate performance metrics
        total_return = (1 + portfolio_returns).prod() - 1
        annualized_return = (1 + total_return) ** (252 / len(portfolio_returns)) - 1
        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # Calculate drawdowns
        cumulative_returns = (1 + portfolio_returns).cumprod()
        running_max = cumulative_returns.cummax()
        drawdowns = (cumulative_returns / running_max - 1)
        max_drawdown = drawdowns.min()
        
        # Calculate win rate
        win_rate = (portfolio_returns > 0).mean()
        
        # Store metrics
        self.performance_metrics = {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'strategy_id': self.strategy_id
        }
        
        return self.performance_metrics
    
    def save_results(self, positions, portfolio_composition, performance_metrics, output_dir):
        """
        Save strategy results to files.
        
        Parameters:
        - positions: DataFrame with portfolio positions over time
        - portfolio_composition: Dictionary with portfolio composition over time
        - performance_metrics: Dictionary with performance metrics
        - output_dir: Directory to save results
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Save positions
        positions.to_csv(f"{output_dir}/positions_{self.strategy_id}.csv")
        
        # Save portfolio composition
        pd.DataFrame({
            'date': portfolio_composition['dates'],
            'positions': [str(p) for p in portfolio_composition['positions']]
        }).to_csv(f"{output_dir}/portfolio_composition_{self.strategy_id}.csv", index=False)
        
        # Save performance metrics
        pd.DataFrame([performance_metrics]).to_csv(f"{output_dir}/performance_{self.strategy_id}.csv", index=False)
        
        logger.info(f"Results saved to {output_dir}")
    
    def backtest(self, output_dir=None):
        """
        Run backtest for the strategy.
        
        Parameters:
        - output_dir: Directory to save results
        
        Returns:
        - Dictionary with performance metrics
        """
        logger.info(f"Starting backtest for {self.strategy_id}")
        
        # Run strategy to get positions
        positions, portfolio_composition = self.run_strategy()
        
        # Get price data
        price_data = self.get_price_data(self.start_date, self.end_date)
        
        # Apply risk management
        adjusted_positions = self.apply_risk_management(positions, price_data)
        
        # Calculate performance
        performance_metrics = self.calculate_performance(adjusted_positions, price_data)
        
        # Save results if output directory is provided
        if output_dir:
            self.save_results(adjusted_positions, portfolio_composition, performance_metrics, output_dir)
        
        logger.info(f"Backtest completed for {self.strategy_id}")
        logger.info(f"Performance: {performance_metrics}")
        
        return performance_metrics
