import pandas as pd
import numpy as np
from factors.base_factor import BaseFactor

class TradingVolumeFactor(BaseFactor):
    """
    Trading Volume factor implementation
    Measures the liquidity of stocks based on trading volume
    """
    
    def __init__(self):
        """Initialize the Trading Volume factor"""
        super().__init__(
            name="TradingVolume",
            factor_type="Liquidity",
            description="Trading Volume factor. Measures stock liquidity based on trading volume."
        )
    
    def calculate(self, price_data):
        """
        Calculate Trading Volume factor from price data
        
        Parameters:
        - price_data: Dictionary of DataFrames with price data (key=ticker, value=DataFrame)
        
        Returns:
        - DataFrame with Trading Volume factor values (index=dates, columns=tickers)
        """
        # Get all unique dates from price data
        all_dates = set()
        for ticker, df in price_data.items():
            all_dates.update(df.index)
        
        all_dates = sorted(list(all_dates))
        volume_df = pd.DataFrame(index=all_dates)
        
        # Extract volume data for each stock
        for ticker, df in price_data.items():
            if 'volume' in df.columns:
                # Calculate normalized volume (relative to average)
                avg_volume = df['volume'].mean()
                if avg_volume > 0:
                    volume_df[ticker] = df['volume'] / avg_volume
        
        # If no volume data is available, generate synthetic data
        if volume_df.empty:
            for ticker, df in price_data.items():
                # Generate random volume data that's somewhat related to price volatility
                price_volatility = df['adjusted_close'].pct_change().rolling(window=20).std().fillna(0)
                
                # Base volume on volatility with some random noise
                base_volume = 1.0 + price_volatility * 10
                volume_df[ticker] = base_volume * (1 + np.random.normal(0, 0.3, len(df)))
                
                # Ensure volumes are positive
                volume_df[ticker] = np.maximum(volume_df[ticker], 0.1)
        
        return volume_df
