import pandas as pd
import numpy as np
from factors.base_factor import BaseFactor

class SMBFactor(BaseFactor):
    """
    Small Minus Big (SMB) Fama-French factor implementation
    Measures the excess return of small-cap stocks over large-cap stocks
    """
    
    def __init__(self):
        """Initialize the SMB factor"""
        super().__init__(
            name="SMB",
            factor_type="Fama-French",
            description="Small Minus Big factor. Measures the excess return of small-cap stocks over large-cap stocks."
        )
    
    def calculate(self, price_data):
        """
        Calculate SMB factor values from market cap data
        
        Parameters:
        - price_data: Dictionary of DataFrames with price data (key=ticker, value=DataFrame)
        
        Returns:
        - DataFrame with SMB values (index=dates, columns=tickers)
        """
        # Get all unique dates from price data
        all_dates = set()
        for ticker, df in price_data.items():
            all_dates.update(df.index)
        
        all_dates = sorted(list(all_dates))
        smb_df = pd.DataFrame(index=all_dates)
        
        # Calculate market cap for each stock
        market_caps = {}
        for ticker, df in price_data.items():
            if 'adjusted_close' in df.columns:
                # Generate random shares outstanding (between 1B and 10B)
                # In a real implementation, this would use actual shares outstanding data
                shares_outstanding = np.random.uniform(1e9, 10e9)
                
                # Calculate market cap as price * shares outstanding
                market_caps[ticker] = df['adjusted_close'] * shares_outstanding
        
        # For each date, calculate the median market cap
        for date in all_dates:
            date_caps = {}
            for ticker, mcap_series in market_caps.items():
                if date in mcap_series.index:
                    date_caps[ticker] = mcap_series.loc[date]
            
            if date_caps:
                # Calculate median market cap
                median_cap = np.median(list(date_caps.values()))
                
                # Assign SMB score based on market cap relative to median
                # Higher score = smaller company (higher SMB exposure)
                for ticker, mcap in date_caps.items():
                    # Normalize to a range around 0
                    # Smaller companies get positive scores, larger companies get negative scores
                    smb_df.loc[date, ticker] = (median_cap / mcap - 1) * 5  # Scale factor
        
        return smb_df


class HMLFactor(BaseFactor):
    """
    High Minus Low (HML) Fama-French factor implementation
    Measures the excess return of value stocks (high book-to-market) over growth stocks (low book-to-market)
    """
    
    def __init__(self):
        """Initialize the HML factor"""
        super().__init__(
            name="HML",
            factor_type="Fama-French",
            description="High Minus Low factor. Measures the excess return of value stocks over growth stocks."
        )
    
    def calculate(self, data):
        """
        Calculate HML factor values from book-to-market data
        
        Parameters:
        - data: Dictionary containing 'book_values' DataFrame
        
        Returns:
        - DataFrame with HML values (index=dates, columns=tickers)
        """
        price_data = data
        
        # Get all unique dates from price data
        all_dates = set()
        for ticker, df in price_data.items():
            all_dates.update(df.index)
        
        all_dates = sorted(list(all_dates))
        hml_df = pd.DataFrame(index=all_dates)
        
        # Generate synthetic book values for each stock
        book_values = {}
        for ticker, df in price_data.items():
            if 'adjusted_close' in df.columns:
                # Generate random book value that's somewhat related to price
                # In a real implementation, this would use actual book value data
                base_book_value = np.random.uniform(0.3, 1.5) * df['adjusted_close'].mean()
                
                # Create a series with some random variation
                book_values[ticker] = pd.Series(
                    base_book_value * (1 + np.random.normal(0, 0.05, len(df))),
                    index=df.index
                )
        
        # Calculate book-to-market ratio for each stock and date
        for date in all_dates:
            date_btm = {}
            for ticker, df in price_data.items():
                if date in df.index and date in book_values[ticker].index:
                    # Book-to-Market = Book Value / Market Price
                    date_btm[ticker] = book_values[ticker].loc[date] / df.loc[date, 'adjusted_close']
            
            if date_btm:
                # Calculate median book-to-market
                median_btm = np.median(list(date_btm.values()))
                
                # Assign HML score based on book-to-market relative to median
                # Higher score = higher book-to-market (higher HML exposure)
                for ticker, btm in date_btm.items():
                    # Normalize to a range around 0
                    # Value stocks (high B/M) get positive scores, growth stocks (low B/M) get negative scores
                    hml_df.loc[date, ticker] = (btm / median_btm - 1) * 5  # Scale factor
        
        return hml_df


class MarketFactor(BaseFactor):
    """
    Market Factor (Rm-Rf) Fama-French factor implementation
    Measures the excess return of the market over the risk-free rate
    """
    
    def __init__(self):
        """Initialize the Market factor"""
        super().__init__(
            name="Rm_Rf",
            factor_type="Fama-French",
            description="Market factor (Rm-Rf). Measures the excess return of the market over the risk-free rate."
        )
    
    def calculate(self, price_data):
        """
        Calculate Market factor values from price data
        
        Parameters:
        - price_data: Dictionary of DataFrames with price data (key=ticker, value=DataFrame)
        
        Returns:
        - DataFrame with Market factor values (index=dates, columns=tickers)
        """
        # Get all unique dates from price data
        all_dates = set()
        for ticker, df in price_data.items():
            all_dates.update(df.index)
        
        all_dates = sorted(list(all_dates))
        market_df = pd.DataFrame(index=all_dates)
        
        # Calculate market returns (equal-weighted average of all stocks)
        market_returns = pd.Series(index=all_dates, dtype=float)
        
        for date in all_dates:
            if date == all_dates[0]:
                market_returns[date] = 0
                continue
                
            prev_date = all_dates[all_dates.index(date) - 1]
            date_returns = []
            
            for ticker, df in price_data.items():
                if date in df.index and prev_date in df.index:
                    # Calculate daily return
                    daily_return = (df.loc[date, 'adjusted_close'] / df.loc[prev_date, 'adjusted_close']) - 1
                    date_returns.append(daily_return)
            
            if date_returns:
                market_returns[date] = np.mean(date_returns)
            else:
                market_returns[date] = 0
        
        # Assume a constant risk-free rate (in a real implementation, this would use actual risk-free rate data)
        risk_free_rate = 0.02 / 252  # Daily risk-free rate (2% annual)
        
        # Calculate market factor (Rm-Rf) for each stock
        for ticker in price_data.keys():
            # Market beta varies by stock (in a real implementation, this would be calculated from historical data)
            beta = np.random.uniform(0.5, 1.5)
            
            # Market factor exposure is proportional to beta
            market_df[ticker] = (market_returns - risk_free_rate) * beta
        
        return market_df
