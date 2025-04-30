"""
Long-Only Strategy Module

This module implements a long-only trading strategy based on factor models.
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

class LongOnlyStrategy(BaseStrategy):
    """
    Long-Only trading strategy based on multiple factors.
    
    This strategy goes long on stocks with high factor scores, without any short positions.
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
                 selection_pct=0.5,
                 min_stocks=5,
                 equal_weight=False,
                 strategy_id=None):
        """
        Initialize the long-only strategy.
        
        Parameters:
        - factor_names: List of factor names to use
        - factor_weights: Dictionary of factor weights (key=factor_name, value=weight)
        - tickers: List of stock tickers to trade
        - start_date: Start date for the strategy (YYYY-MM-DD)
        - end_date: End date for the strategy (YYYY-MM-DD)
        - rebalance_freq: Rebalancing frequency ('D'=daily, 'W'=weekly, 'M'=monthly)
        - stop_loss: Stop loss percentage (e.g., 0.05 for 5%)
        - take_profit: Take profit percentage (e.g., 0.10 for 10%)
        - selection_pct: Percentage of stocks to select (e.g., 0.5 for top 50%)
        - min_stocks: Minimum number of stocks to include
        - equal_weight: If True, use equal weighting instead of market cap weighting
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
        
        # Set long-only specific parameters
        self.selection_pct = selection_pct
        self.min_stocks = min_stocks
        self.equal_weight = equal_weight
        
        logger.info(f"Initialized LongOnlyStrategy with selection_pct={selection_pct}, min_stocks={min_stocks}")
    
    def construct_portfolio(self, date, factor_score, market_cap):
        """
        Construct long-only portfolio based on factor scores.
        
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
            selection_count = max(int(len(sorted_stocks) * self.selection_pct), self.min_stocks)
            selection_count = min(selection_count, len(sorted_stocks))  # Ensure we don't exceed available stocks
            selected_stocks = sorted_stocks.index[:selection_count]
            
            # Calculate weights
            if self.equal_weight:
                # Equal weighting
                weights = pd.Series(1.0 / selection_count, index=selected_stocks)
            else:
                # Market cap weighting
                selected_market_cap = market_cap[selected_stocks]
                weights = selected_market_cap / selected_market_cap.sum() if selected_market_cap.sum() > 0 else pd.Series(1/len(selected_stocks), index=selected_stocks)
            
            # Create positions for all tickers (initialize with zeros)
            all_positions = pd.Series(0, index=self.tickers)
            
            # Update with selected positions
            all_positions.update(weights)
            
            return {
                'positions': all_positions,
                'selected_stocks': list(selected_stocks),
                'weights': weights,
                'date': date
            }
        except Exception as e:
            logger.error(f"Error constructing long-only portfolio for {date}: {e}")
            print(traceback.format_exc())  # Print full traceback
            # Return empty portfolio as fallback
            all_positions = pd.Series(0, index=self.tickers)
            return {
                'positions': all_positions,
                'selected_stocks': [],
                'weights': pd.Series(),
                'date': date,
                'error': str(e)
            }
