import yfinance as yf
import pandas as pd
import sys
import os
# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from config.intervals import get_source_interval, get_resample_rule, needs_resampling

def fetch_ohlcv(ticker: str, start_date: str, end_date: str, interval: str) -> pd.DataFrame:
    """
    Fetches OHLCV data for a given ticker and date range.
    Handles resampling for intervals not natively supported by yfinance.

    Args:
        ticker: The stock ticker symbol.
        start_date: The start date in YYYY-MM-DD format.
        end_date: The end date in YYYY-MM-DD format.
        interval: The desired data interval (e.g., '15m', '45m', '4h').

    Returns:
        A pandas DataFrame with the OHLCV data.
    """
    # Get the source interval to fetch from yfinance
    source_interval = get_source_interval(interval)
    
    # Fetch data from yfinance
    data = yf.download(ticker, start=start_date, end=end_date, interval=source_interval)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)
    
    # Resample if needed
    if needs_resampling(interval):
        resample_rule = get_resample_rule(interval)
        data = resample_ohlcv(data, resample_rule)
    
    return data

def resample_ohlcv(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    """
    Resamples OHLCV data to a different timeframe.
    
    Args:
        df: DataFrame with OHLCV data
        rule: Pandas resample rule (e.g., '45min', '4H')
        
    Returns:
        Resampled DataFrame
    """
    if df.empty:
        return df
    
    resampled = df.resample(rule).agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna()
    
    return resampled

if __name__ == '__main__':
    # Example usage
    ticker = 'AAPL'
    start_date = '2023-01-01'
    end_date = '2023-01-31'
    interval = '1d'

    try:
        ohlcv_data = fetch_ohlcv(ticker, start_date, end_date, interval)
        if not ohlcv_data.empty:
            print(f"Successfully fetched data for {ticker}")
            print(ohlcv_data.head())
        else:
            print(f"No data found for {ticker} in the specified date range.")
    except Exception as e:
        print(f"An error occurred: {e}")
