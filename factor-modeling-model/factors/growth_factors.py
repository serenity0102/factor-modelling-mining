import pandas as pd
import numpy as np
from factors.base_factor import BaseFactor

class RevenueGrowthFactor(BaseFactor):
    """
    Revenue Growth factor implementation
    Measures a company's revenue growth rate
    """
    
    def __init__(self, window=4):
        """
        Initialize the Revenue Growth factor
        
        Parameters:
        - window: Number of quarters to calculate growth (default: 4 quarters/1 year)
        """
        self.window = window
        super().__init__(
            name="RevenueGrowth",
            factor_type="Growth",
            description=f"Revenue Growth over {window} quarters. Measures a company's revenue growth rate."
        )
    
    def calculate(self, price_data):
        """
        Calculate Revenue Growth from synthetic financial data
        
        Parameters:
        - price_data: Dictionary of DataFrames with price data (key=ticker, value=DataFrame)
        
        Returns:
        - DataFrame with Revenue Growth values (index=dates, columns=tickers)
        """
        # Get all unique dates from price data
        all_dates = set()
        for ticker, df in price_data.items():
            all_dates.update(df.index)
        
        all_dates = sorted(list(all_dates))
        growth_df = pd.DataFrame(index=all_dates)
        
        # Generate synthetic quarterly revenue data for each stock
        quarterly_revenues = {}
        
        for ticker, df in price_data.items():
            # Generate base quarterly revenue (related to price)
            base_revenue = np.mean(df['adjusted_close']) * 1e6  # Scale factor
            
            # Create quarterly dates (assuming daily data)
            quarterly_dates = pd.date_range(
                start=df.index.min(),
                end=df.index.max(),
                freq='Q'
            )
            
            # Generate quarterly revenue with growth trend and seasonality
            trend_growth = np.random.uniform(0.01, 0.05)  # 1-5% quarterly growth
            quarterly_trend = (1 + trend_growth) ** np.arange(len(quarterly_dates))
            
            # Add seasonality (Q4 typically higher)
            seasonality = np.array([0.9, 0.95, 1.0, 1.15] * (len(quarterly_dates) // 4 + 1))[:len(quarterly_dates)]
            
            # Add random noise
            noise = 1 + np.random.normal(0, 0.03, len(quarterly_dates))
            
            # Calculate quarterly revenue
            quarterly_revenue = base_revenue * quarterly_trend * seasonality * noise
            
            # Store in dictionary
            quarterly_revenues[ticker] = pd.Series(quarterly_revenue, index=quarterly_dates)
        
        # Calculate revenue growth for each stock and date
        for ticker, df in price_data.items():
            if ticker in quarterly_revenues:
                # For each date, find the most recent quarter and calculate growth
                for date in df.index:
                    # Find the most recent quarter
                    recent_quarter = quarterly_revenues[ticker].index[quarterly_revenues[ticker].index <= date]
                    
                    if len(recent_quarter) >= self.window + 1:
                        recent_quarter = recent_quarter[-1]
                        prev_quarter = quarterly_revenues[ticker].index[-self.window - 1]
                        
                        # Calculate year-over-year growth
                        recent_revenue = quarterly_revenues[ticker][recent_quarter]
                        prev_revenue = quarterly_revenues[ticker][prev_quarter]
                        
                        if prev_revenue > 0:
                            growth = (recent_revenue / prev_revenue) - 1
                            growth_df.loc[date, ticker] = growth
        
        return growth_df
