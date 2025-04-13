import pandas as pd
import numpy as np
from factors.base_factor import BaseFactor

class InventoryTurnoverFactor(BaseFactor):
    """
    Inventory Turnover factor implementation
    Measures how efficiently a company manages its inventory
    """
    
    def __init__(self):
        """Initialize the Inventory Turnover factor"""
        super().__init__(
            name="InventoryTurnover",
            factor_type="Operational",
            description="Inventory Turnover (Cost of Goods Sold / Average Inventory). Measures how efficiently a company manages its inventory."
        )
    
    def calculate(self, price_data):
        """
        Calculate Inventory Turnover from synthetic financial data
        
        Parameters:
        - price_data: Dictionary of DataFrames with price data (key=ticker, value=DataFrame)
        
        Returns:
        - DataFrame with Inventory Turnover values (index=dates, columns=tickers)
        """
        # Get all unique dates from price data
        all_dates = set()
        for ticker, df in price_data.items():
            all_dates.update(df.index)
        
        all_dates = sorted(list(all_dates))
        it_df = pd.DataFrame(index=all_dates)
        
        # Generate synthetic inventory turnover data for each stock
        for ticker, df in price_data.items():
            # Generate base inventory turnover (varies by industry, typically between 2 and 20)
            base_it = np.random.uniform(2.0, 20.0)
            
            # Create a series with some random variation over time
            # Use random walk with mean reversion
            random_changes = np.random.normal(0, 0.05, len(df))
            mean_reversion = 0.05 * (base_it - np.cumsum(random_changes))
            it_series = base_it + np.cumsum(random_changes + mean_reversion)
            
            # Ensure inventory turnover values are positive and reasonable
            it_series = np.clip(it_series, 1.0, 30.0)
            
            # Add to DataFrame
            it_df[ticker] = pd.Series(it_series, index=df.index)
        
        return it_df


class GrossProfitMarginFactor(BaseFactor):
    """
    Gross Profit Margin factor implementation
    Measures a company's manufacturing and distribution efficiency
    """
    
    def __init__(self):
        """Initialize the Gross Profit Margin factor"""
        super().__init__(
            name="GrossProfitMargin",
            factor_type="Operational",
            description="Gross Profit Margin ((Revenue - COGS) / Revenue). Measures a company's manufacturing and distribution efficiency."
        )
    
    def calculate(self, price_data):
        """
        Calculate Gross Profit Margin from synthetic financial data
        
        Parameters:
        - price_data: Dictionary of DataFrames with price data (key=ticker, value=DataFrame)
        
        Returns:
        - DataFrame with Gross Profit Margin values (index=dates, columns=tickers)
        """
        # Get all unique dates from price data
        all_dates = set()
        for ticker, df in price_data.items():
            all_dates.update(df.index)
        
        all_dates = sorted(list(all_dates))
        gpm_df = pd.DataFrame(index=all_dates)
        
        # Generate synthetic gross profit margin data for each stock
        for ticker, df in price_data.items():
            # Generate base gross profit margin (typically between 0.2 and 0.6)
            base_gpm = np.random.uniform(0.2, 0.6)
            
            # Create a series with some random variation over time
            # Use random walk with mean reversion
            random_changes = np.random.normal(0, 0.005, len(df))
            mean_reversion = 0.05 * (base_gpm - np.cumsum(random_changes))
            gpm_series = base_gpm + np.cumsum(random_changes + mean_reversion)
            
            # Ensure gross profit margin values are reasonable
            gpm_series = np.clip(gpm_series, 0.05, 0.8)
            
            # Add to DataFrame
            gpm_df[ticker] = pd.Series(gpm_series, index=df.index)
        
        return gpm_df
