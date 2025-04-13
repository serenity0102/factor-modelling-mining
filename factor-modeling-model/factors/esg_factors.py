import pandas as pd
import numpy as np
from factors.base_factor import BaseFactor

class BoardAgeFactor(BaseFactor):
    """
    Average Age of Board of Directors factor implementation
    Measures the average age of a company's board members
    """
    
    def __init__(self):
        """Initialize the Board Age factor"""
        super().__init__(
            name="BoardAge",
            factor_type="Governance",
            description="Average Age of Board of Directors. Measures the average age of a company's board members."
        )
    
    def calculate(self, price_data):
        """
        Calculate Average Board Age from synthetic governance data
        
        Parameters:
        - price_data: Dictionary of DataFrames with price data (key=ticker, value=DataFrame)
        
        Returns:
        - DataFrame with Board Age values (index=dates, columns=tickers)
        """
        # Get all unique dates from price data
        all_dates = set()
        for ticker, df in price_data.items():
            all_dates.update(df.index)
        
        all_dates = sorted(list(all_dates))
        age_df = pd.DataFrame(index=all_dates)
        
        # Generate synthetic board age data for each stock
        for ticker, df in price_data.items():
            # Generate base board age (typically between 55 and 65)
            base_age = np.random.uniform(55, 65)
            
            # Create a series with minimal variation over time
            # Board composition changes slowly
            random_changes = np.random.normal(0, 0.01, len(df))
            age_series = base_age + np.cumsum(random_changes)
            
            # Ensure ages are reasonable
            age_series = np.clip(age_series, 50, 70)
            
            # Add to DataFrame
            age_df[ticker] = pd.Series(age_series, index=df.index)
        
        return age_df


class ExecutiveCompensationFactor(BaseFactor):
    """
    Executive Compensation to Revenue Ratio factor implementation
    Measures the ratio of executive compensation to company revenue
    """
    
    def __init__(self):
        """Initialize the Executive Compensation factor"""
        super().__init__(
            name="ExecCompToRevenue",
            factor_type="ESG Governance",
            description="Executive Compensation to Revenue Ratio. Measures the ratio of executive compensation to company revenue."
        )
    
    def calculate(self, price_data):
        """
        Calculate Executive Compensation to Revenue Ratio from synthetic data
        
        Parameters:
        - price_data: Dictionary of DataFrames with price data (key=ticker, value=DataFrame)
        
        Returns:
        - DataFrame with Executive Compensation to Revenue values (index=dates, columns=tickers)
        """
        # Get all unique dates from price data
        all_dates = set()
        for ticker, df in price_data.items():
            all_dates.update(df.index)
        
        all_dates = sorted(list(all_dates))
        comp_df = pd.DataFrame(index=all_dates)
        
        # Generate synthetic revenue data for each stock
        revenues = {}
        for ticker, df in price_data.items():
            # Generate base revenue (related to price)
            base_revenue = np.mean(df['adjusted_close']) * 1e6  # Scale factor
            
            # Create a series with some random variation over time
            revenue_series = base_revenue * (1 + np.random.normal(0, 0.02, len(df))).cumsum()
            
            # Ensure revenues are positive
            revenue_series = np.maximum(revenue_series, 1e5)
            
            # Store in dictionary
            revenues[ticker] = pd.Series(revenue_series, index=df.index)
        
        # Generate synthetic executive compensation data for each stock
        for ticker, df in price_data.items():
            if ticker in revenues:
                # Generate base compensation ratio (typically between 0.001 and 0.01)
                base_ratio = np.random.uniform(0.001, 0.01)
                
                # Create a series with some random variation over time
                ratio_series = base_ratio * (1 + np.random.normal(0, 0.05, len(df)))
                
                # Ensure ratios are reasonable
                ratio_series = np.clip(ratio_series, 0.0005, 0.02)
                
                # Add to DataFrame
                comp_df[ticker] = pd.Series(ratio_series, index=df.index)
        
        return comp_df


class EnvironmentRatingFactor(BaseFactor):
    """
    Environment Friendly Rating factor implementation
    Measures a company's environmental sustainability rating
    """
    
    def __init__(self):
        """Initialize the Environment Rating factor"""
        super().__init__(
            name="EnvRating",
            factor_type="ESG Environmental",
            description="Environment Friendly Rating. Measures a company's environmental sustainability rating."
        )
    
    def calculate(self, price_data):
        """
        Calculate Environment Rating from synthetic ESG data
        
        Parameters:
        - price_data: Dictionary of DataFrames with price data (key=ticker, value=DataFrame)
        
        Returns:
        - DataFrame with Environment Rating values (index=dates, columns=tickers)
        """
        # Get all unique dates from price data
        all_dates = set()
        for ticker, df in price_data.items():
            all_dates.update(df.index)
        
        all_dates = sorted(list(all_dates))
        env_df = pd.DataFrame(index=all_dates)
        
        # Generate synthetic environment rating data for each stock
        for ticker, df in price_data.items():
            # Generate base rating (scale of 0-100)
            base_rating = np.random.uniform(40, 80)
            
            # Create a series with minimal variation over time
            # ESG ratings change slowly
            random_changes = np.random.normal(0, 0.2, len(df))
            rating_series = base_rating + np.cumsum(random_changes)
            
            # Ensure ratings are within reasonable range
            rating_series = np.clip(rating_series, 0, 100)
            
            # Add to DataFrame
            env_df[ticker] = pd.Series(rating_series, index=df.index)
        
        return env_df
