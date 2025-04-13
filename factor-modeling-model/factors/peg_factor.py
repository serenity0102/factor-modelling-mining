import pandas as pd
import numpy as np
from factors.base_factor import BaseFactor

class PEGFactor(BaseFactor):
    """PEG (Price/Earnings to Growth) factor implementation"""
    
    def __init__(self):
        """Initialize the PEG factor"""
        super().__init__(
            name="PEG",
            factor_type="Fundamental",
            description="Price-to-Earnings to Growth ratio. Lower PEG indicates better value relative to growth."
        )
    
    def calculate(self, data):
        """
        Calculate PEG ratio from P/E and growth data
        
        Parameters:
        - data: Dictionary containing 'pe_ratios' and 'growth_rates' DataFrames
        
        Returns:
        - DataFrame with PEG values (index=dates, columns=tickers)
        """
        pe_df = data.get('pe_ratios')
        growth_df = data.get('growth_rates')
        
        if pe_df is None or growth_df is None:
            raise ValueError("PEG calculation requires 'pe_ratios' and 'growth_rates' in data dictionary")
        
        peg_df = pd.DataFrame(index=pe_df.index)
        
        for ticker in pe_df.columns:
            if ticker in growth_df.columns:
                # PEG = P/E / Growth rate
                peg_df[ticker] = pe_df[ticker] / (growth_df[ticker] * 100)  # Convert growth to percentage
        
        return peg_df
