"""
Long-Short Strategy Module

This module implements a long-short trading strategy based on factor models.
"""

import pandas as pd
import numpy as np
import logging
import traceback
from strategy.base_strategy import BaseStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LongShortStrategy(BaseStrategy):
    """
    Long-Short trading strategy based on multiple factors.
    
    This strategy goes long on stocks with high factor scores and short on stocks with low factor scores.
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
                 long_pct=0.4,
                 short_pct=0.2,
                 long_allocation=0.8,
                 short_allocation=0.5,
                 strategy_id=None):
        """
        Initialize the long-short strategy.
        
        Parameters:
        - factor_names: List of factor names to use
        - factor_weights: Dictionary of factor weights (key=factor_name, value=weight)
        - tickers: List of stock tickers to trade
        - start_date: Start date for the strategy (YYYY-MM-DD)
        - end_date: End date for the strategy (YYYY-MM-DD)
        - rebalance_freq: Rebalancing frequency ('D'=daily, 'W'=weekly, 'M'=monthly)
        - stop_loss: Stop loss percentage (e.g., 0.05 for 5%)
        - take_profit: Take profit percentage (e.g., 0.10 for 10%)
        - long_pct: Percentage of stocks to go long (e.g., 0.4 for top 40%)
        - short_pct: Percentage of stocks to go short (e.g., 0.2 for bottom 20%)
        - long_allocation: Percentage of capital for long positions (e.g., 0.8 for 80%)
        - short_allocation: Percentage of capital for short positions (e.g., 0.5 for 50%)
        - strategy_id: Unique identifier for the strategy instance
        """
        # Initialize base strategy
        super().__init__(
            factor_names=factor_names,
            factor_weights=factor_weights,
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            rebalance_freq=rebalance_freq,
            stop_loss=stop_loss,
            take_profit=take_profit,
            strategy_id=strategy_id
        )
        
        # Set long-short specific parameters
        self.long_pct = long_pct
        self.short_pct = short_pct
        self.long_allocation = long_allocation
        self.short_allocation = short_allocation
        
        logger.info(f"Initialized LongShortStrategy with long_pct={long_pct}, short_pct={short_pct}")
    
    def construct_portfolio(self, date, factor_score, market_cap):
        """
        Construct long-short portfolio based on factor scores.
        
        Parameters:
        - date: Date to construct portfolio for (YYYY-MM-DD)
        - factor_score: Series with factor scores for each stock
        - market_cap: Series with market cap values for each stock
        
        Returns:
        - Dictionary with portfolio positions and metadata
        """
        try:
            # Sort stocks by factor score
            sorted_stocks = factor_score.sort_values(ascending=False)
            
            # Select top stocks for long positions
            long_count = int(len(sorted_stocks) * self.long_pct)
            long_stocks = sorted_stocks.index[:long_count]
            
            # Select bottom stocks for short positions
            short_count = int(len(sorted_stocks) * self.short_pct)
            short_stocks = sorted_stocks.index[-short_count:]
            
            # Calculate market cap weights
            long_market_cap = market_cap[long_stocks]
            short_market_cap = market_cap[short_stocks]
            
            # Normalize weights to sum to 1
            long_weights = long_market_cap / long_market_cap.sum() if long_market_cap.sum() > 0 else pd.Series(1/len(long_stocks), index=long_stocks)
            short_weights = short_market_cap / short_market_cap.sum() if short_market_cap.sum() > 0 else pd.Series(1/len(short_stocks), index=short_stocks)
            
            # Scale weights by target allocation
            long_positions = long_weights * self.long_allocation
            short_positions = short_weights * self.short_allocation * -1  # Negative for short positions
            
            # Combine positions
            all_positions = pd.Series(0, index=self.tickers)
            all_positions.update(long_positions)
            all_positions.update(short_positions)
            
            return {
                'positions': all_positions,
                'long_stocks': list(long_stocks),
                'short_stocks': list(short_stocks),
                'long_weights': long_positions,
                'short_weights': short_positions,
                'date': date
            }
        except Exception as e:
            logger.error(f"Error constructing long-short portfolio for {date}: {e}")
            print(traceback.format_exc())  # Print full traceback
            # Return empty portfolio as fallback
            all_positions = pd.Series(0, index=self.tickers)
            return {
                'positions': all_positions,
                'long_stocks': [],
                'short_stocks': [],
                'long_weights': pd.Series(),
                'short_weights': pd.Series(),
                'date': date,
                'error': str(e)
            }
