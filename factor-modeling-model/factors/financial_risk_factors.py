import pandas as pd
import numpy as np
from factors.base_factor import BaseFactor

class DebtToEquityFactor(BaseFactor):
    """
    Debt-to-Equity Ratio factor implementation
    Measures a company's financial leverage
    """
    
    def __init__(self):
        """Initialize the Debt-to-Equity factor"""
        super().__init__(
            name="DebtToEquity",
            factor_type="Financial Risk",
            description="Debt-to-Equity Ratio (Total Debt / Shareholders' Equity). Measures a company's financial leverage."
        )
    
    def calculate(self, price_data):
        """
        Calculate Debt-to-Equity Ratio from synthetic financial data
        
        Parameters:
        - price_data: Dictionary of DataFrames with price data (key=ticker, value=DataFrame)
        
        Returns:
        - DataFrame with Debt-to-Equity values (index=dates, columns=tickers)
        """
        # Get all unique dates from price data
        all_dates = set()
        for ticker, df in price_data.items():
            all_dates.update(df.index)
        
        all_dates = sorted(list(all_dates))
        de_df = pd.DataFrame(index=all_dates)
        
        # Generate synthetic debt-to-equity data for each stock
        for ticker, df in price_data.items():
            # Generate base debt-to-equity ratio (typically between 0.3 and 2.0)
            base_de = np.random.uniform(0.3, 2.0)
            
            # Create a series with some random variation over time
            # Use random walk with mean reversion
            random_changes = np.random.normal(0, 0.01, len(df))
            mean_reversion = 0.05 * (base_de - np.cumsum(random_changes))
            de_series = base_de + np.cumsum(random_changes + mean_reversion)
            
            # Ensure debt-to-equity values are positive and reasonable
            de_series = np.clip(de_series, 0.1, 3.0)
            
            # Add to DataFrame
            de_df[ticker] = pd.Series(de_series, index=df.index)
        
        return de_df


class InterestCoverageFactor(BaseFactor):
    """
    Interest Coverage Ratio factor implementation
    Measures a company's ability to pay interest on its debt
    """
    
    def __init__(self):
        """Initialize the Interest Coverage factor"""
        super().__init__(
            name="InterestCoverage",
            factor_type="Financial Risk",
            description="Interest Coverage Ratio (EBIT / Interest Expense). Measures a company's ability to pay interest on its debt."
        )
    
    def calculate(self, price_data):
        """
        Calculate Interest Coverage Ratio from synthetic financial data
        
        Parameters:
        - price_data: Dictionary of DataFrames with price data (key=ticker, value=DataFrame)
        
        Returns:
        - DataFrame with Interest Coverage values (index=dates, columns=tickers)
        """
        # Get all unique dates from price data
        all_dates = set()
        for ticker, df in price_data.items():
            all_dates.update(df.index)
        
        all_dates = sorted(list(all_dates))
        ic_df = pd.DataFrame(index=all_dates)
        
        # Generate synthetic interest coverage data for each stock
        for ticker, df in price_data.items():
            # Generate base interest coverage ratio (typically between 2.0 and 15.0)
            base_ic = np.random.uniform(2.0, 15.0)
            
            # Create a series with some random variation over time
            # Use random walk with mean reversion
            random_changes = np.random.normal(0, 0.1, len(df))
            mean_reversion = 0.05 * (base_ic - np.cumsum(random_changes))
            ic_series = base_ic + np.cumsum(random_changes + mean_reversion)
            
            # Ensure interest coverage values are reasonable
            ic_series = np.clip(ic_series, 0.5, 25.0)
            
            # Add to DataFrame
            ic_df[ticker] = pd.Series(ic_series, index=df.index)
        
        return ic_df
