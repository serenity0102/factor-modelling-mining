import pandas as pd
import numpy as np
from factors.base_factor import BaseFactor

class CurrentRatioFactor(BaseFactor):
    """
    Current Ratio factor implementation
    Measures a company's ability to pay short-term obligations
    """
    
    def __init__(self):
        """Initialize the Current Ratio factor"""
        super().__init__(
            name="CurrentRatio",
            factor_type="Financial Health",
            description="Current Ratio (Current Assets / Current Liabilities). Measures a company's ability to pay short-term obligations."
        )
    
    def calculate(self, price_data):
        """
        Calculate Current Ratio from synthetic financial data
        
        Parameters:
        - price_data: Dictionary of DataFrames with price data (key=ticker, value=DataFrame)
        
        Returns:
        - DataFrame with Current Ratio values (index=dates, columns=tickers)
        """
        # Get all unique dates from price data
        all_dates = set()
        for ticker, df in price_data.items():
            all_dates.update(df.index)
        
        all_dates = sorted(list(all_dates))
        cr_df = pd.DataFrame(index=all_dates)
        
        # Generate synthetic current ratio data for each stock
        for ticker, df in price_data.items():
            # Generate base current ratio (typically between 1.0 and 3.0)
            base_cr = np.random.uniform(1.0, 3.0)
            
            # Create a series with some random variation over time
            # Use random walk with mean reversion
            random_changes = np.random.normal(0, 0.02, len(df))
            mean_reversion = 0.05 * (base_cr - np.cumsum(random_changes))
            cr_series = base_cr + np.cumsum(random_changes + mean_reversion)
            
            # Ensure current ratios are positive and reasonable
            cr_series = np.clip(cr_series, 0.5, 5.0)
            
            # Add to DataFrame
            cr_df[ticker] = pd.Series(cr_series, index=df.index)
        
        return cr_df


class CashRatioFactor(BaseFactor):
    """
    Cash Ratio factor implementation
    Measures a company's ability to cover short-term liabilities with cash and cash equivalents
    """
    
    def __init__(self):
        """Initialize the Cash Ratio factor"""
        super().__init__(
            name="CashRatio",
            factor_type="Financial Health",
            description="Cash Ratio (Cash & Equivalents / Current Liabilities). Measures a company's ability to cover short-term liabilities with cash."
        )
    
    def calculate(self, price_data):
        """
        Calculate Cash Ratio from synthetic financial data
        
        Parameters:
        - price_data: Dictionary of DataFrames with price data (key=ticker, value=DataFrame)
        
        Returns:
        - DataFrame with Cash Ratio values (index=dates, columns=tickers)
        """
        # Get all unique dates from price data
        all_dates = set()
        for ticker, df in price_data.items():
            all_dates.update(df.index)
        
        all_dates = sorted(list(all_dates))
        cash_ratio_df = pd.DataFrame(index=all_dates)
        
        # Generate synthetic cash ratio data for each stock
        for ticker, df in price_data.items():
            # Generate base cash ratio (typically between 0.2 and 1.0)
            base_cash_ratio = np.random.uniform(0.2, 1.0)
            
            # Create a series with some random variation over time
            # Use random walk with mean reversion
            random_changes = np.random.normal(0, 0.01, len(df))
            mean_reversion = 0.05 * (base_cash_ratio - np.cumsum(random_changes))
            cash_ratio_series = base_cash_ratio + np.cumsum(random_changes + mean_reversion)
            
            # Ensure cash ratios are positive and reasonable
            cash_ratio_series = np.clip(cash_ratio_series, 0.05, 2.0)
            
            # Add to DataFrame
            cash_ratio_df[ticker] = pd.Series(cash_ratio_series, index=df.index)
        
        return cash_ratio_df
