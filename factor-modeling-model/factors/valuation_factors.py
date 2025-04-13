import pandas as pd
import numpy as np
from factors.base_factor import BaseFactor

class PBFactor(BaseFactor):
    """
    Price-to-Book (P/B) factor implementation
    Measures the ratio of stock price to book value per share
    """
    
    def __init__(self):
        """Initialize the P/B factor"""
        super().__init__(
            name="PB",
            factor_type="Valuation",
            description="Price-to-Book ratio. Lower P/B indicates potentially undervalued stocks."
        )
    
    def calculate(self, price_data):
        """
        Calculate P/B ratio from price data and synthetic book values
        
        Parameters:
        - price_data: Dictionary of DataFrames with price data (key=ticker, value=DataFrame)
        
        Returns:
        - DataFrame with P/B values (index=dates, columns=tickers)
        """
        # Get all unique dates from price data
        all_dates = set()
        for ticker, df in price_data.items():
            all_dates.update(df.index)
        
        all_dates = sorted(list(all_dates))
        pb_df = pd.DataFrame(index=all_dates)
        
        # Generate synthetic book values for each stock
        for ticker, df in price_data.items():
            if 'adjusted_close' in df.columns:
                # Generate random book value that's somewhat related to price
                # In a real implementation, this would use actual book value data
                base_book_value = np.random.uniform(0.2, 0.8) * df['adjusted_close'].mean()
                
                # Create a series with some random variation over time
                book_values = pd.Series(
                    base_book_value * (1 + np.random.normal(0, 0.02, len(df))).cumsum(),
                    index=df.index
                )
                
                # Ensure book values are positive
                book_values = np.maximum(book_values, 0.1)
                
                # Calculate P/B ratio
                pb_df[ticker] = df['adjusted_close'] / book_values
        
        return pb_df
