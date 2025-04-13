import pandas as pd
import numpy as np
from factors.base_factor import BaseFactor
from factors.rsi_factor import RSIFactor

class ROCFactor(BaseFactor):
    """
    Rate of Change (ROC) factor implementation
    Measures price momentum over a specified period
    """
    
    def __init__(self, window=20):
        """
        Initialize the ROC factor
        
        Parameters:
        - window: ROC calculation window (default: 20 days)
        """
        self.window = window
        super().__init__(
            name=f"ROC{window}",
            factor_type="Technical",
            description=f"Rate of Change with {window}-day window. Measures price momentum over time."
        )
    
    def calculate(self, price_data):
        """
        Calculate ROC values from price data
        
        Parameters:
        - price_data: Dictionary of DataFrames with price data (key=ticker, value=DataFrame)
        
        Returns:
        - DataFrame with ROC values (index=dates, columns=tickers)
        """
        # Get all unique dates from price data
        all_dates = set()
        for ticker, df in price_data.items():
            all_dates.update(df.index)
        
        all_dates = sorted(list(all_dates))
        roc_df = pd.DataFrame(index=all_dates)
        
        for ticker, df in price_data.items():
            if 'adjusted_close' in df.columns:
                # Calculate ROC: ((Price_t / Price_(t-n)) - 1) * 100
                roc = (df['adjusted_close'] / df['adjusted_close'].shift(self.window) - 1) * 100
                roc_df[ticker] = roc
        
        return roc_df
