import pandas as pd
import numpy as np
from factors.base_factor import BaseFactor

class AverageSentimentFactor(BaseFactor):
    """
    Average Sentiment factor implementation
    Measures the average sentiment of news and social media about a company
    """
    
    def __init__(self, window=14):
        """
        Initialize the Average Sentiment factor
        
        Parameters:
        - window: Number of days to average sentiment (default: 14 days)
        """
        self.window = window
        super().__init__(
            name=f"AvgSentiment{window}",
            factor_type="Sentiment",
            description=f"Average Sentiment over {window} days. Measures the average sentiment of news and social media about a company."
        )
    
    def calculate(self, price_data):
        """
        Calculate Average Sentiment from synthetic sentiment data
        
        Parameters:
        - price_data: Dictionary of DataFrames with price data (key=ticker, value=DataFrame)
        
        Returns:
        - DataFrame with Average Sentiment values (index=dates, columns=tickers)
        """
        # Get all unique dates from price data
        all_dates = set()
        for ticker, df in price_data.items():
            all_dates.update(df.index)
        
        all_dates = sorted(list(all_dates))
        sentiment_df = pd.DataFrame(index=all_dates)
        
        # Generate synthetic daily sentiment data for each stock
        daily_sentiment = {}
        
        for ticker, df in price_data.items():
            # Generate base sentiment (scale of -1 to 1)
            base_sentiment = np.random.uniform(-0.2, 0.2)
            
            # Create a series with random variation
            # Sentiment is somewhat correlated with price changes
            price_changes = df['adjusted_close'].pct_change().fillna(0)
            
            # Mix of price correlation and random noise
            sentiment_series = base_sentiment + 0.5 * price_changes + np.random.normal(0, 0.1, len(df))
            
            # Ensure sentiment is within -1 to 1 range
            sentiment_series = np.clip(sentiment_series, -1, 1)
            
            # Store in dictionary
            daily_sentiment[ticker] = pd.Series(sentiment_series, index=df.index)
        
        # Calculate rolling average sentiment for each stock
        for ticker, sentiment_series in daily_sentiment.items():
            # Calculate rolling average
            rolling_sentiment = sentiment_series.rolling(window=self.window, min_periods=1).mean()
            
            # Add to DataFrame
            sentiment_df[ticker] = rolling_sentiment
        
        return sentiment_df
