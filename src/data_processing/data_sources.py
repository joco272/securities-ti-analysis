"""
Data Source Abstraction Layer

This module provides a unified interface for fetching market data from multiple sources:
- yfinance
- finnhub
- polygon.io
- alphavantage

The data source can be configured in config/settings.py
"""
import os
import pandas as pd
from typing import Optional
import logging

from config.settings import (
    PRIMARY_DATA_SOURCE,
    FINNHUB_API_KEY,
    POLYGON_API_KEY,
    ALPHAVANTAGE_API_KEY
)

logger = logging.getLogger(__name__)


class DataSourceError(Exception):
    """Custom exception for data source errors."""
    pass


def fetch_from_yfinance(ticker: str, start_date: str, end_date: str, interval: str) -> pd.DataFrame:
    """
    Fetch data using yfinance.
    
    Args:
        ticker: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval (e.g., '5m', '15m', '1h', '1d')
    
    Returns:
        DataFrame with OHLCV data
    """
    import yfinance as yf
    
    try:
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval, progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        return data
    except Exception as e:
        logger.error(f"Error fetching from yfinance for {ticker}: {e}")
        return pd.DataFrame()


def fetch_from_finnhub(ticker: str, start_date: str, end_date: str, interval: str) -> pd.DataFrame:
    """
    Fetch data using Finnhub API.
    
    Note: Finnhub requires API key and has specific interval format.
    
    Args:
        ticker: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval
    
    Returns:
        DataFrame with OHLCV data
    """
    api_key = os.environ.get('FINNHUB_API_KEY', FINNHUB_API_KEY)
    
    if not api_key:
        raise DataSourceError("Finnhub API key not configured")
    
    try:
        import finnhub
        from datetime import datetime
        
        client = finnhub.Client(api_key=api_key)
        
        # Convert interval to Finnhub format
        interval_map = {
            '1m': '1', '5m': '5', '15m': '15', '30m': '30',
            '1h': '60', '1d': 'D', '1w': 'W', '1M': 'M'
        }
        fh_interval = interval_map.get(interval, 'D')
        
        # Convert dates to timestamps
        start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        
        # Fetch data
        res = client.stock_candles(ticker, fh_interval, start_ts, end_ts)
        
        if res['s'] != 'ok':
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame({
            'Open': res['o'],
            'High': res['h'],
            'Low': res['l'],
            'Close': res['c'],
            'Volume': res['v']
        }, index=pd.to_datetime(res['t'], unit='s'))
        
        return df
        
    except ImportError:
        raise DataSourceError("finnhub-python package not installed. Install with: pip install finnhub-python")
    except Exception as e:
        logger.error(f"Error fetching from Finnhub: {e}")
        return pd.DataFrame()


def fetch_from_polygon(ticker: str, start_date: str, end_date: str, interval: str) -> pd.DataFrame:
    """
    Fetch data using Polygon.io API.
    
    Note: Polygon requires API key.
    
    Args:
        ticker: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval
    
    Returns:
        DataFrame with OHLCV data
    """
    api_key = os.environ.get('POLYGON_API_KEY', POLYGON_API_KEY)
    
    if not api_key:
        raise DataSourceError("Polygon API key not configured")
    
    try:
        from polygon import RESTClient
        from datetime import datetime
        
        client = RESTClient(api_key)
        
        # Convert interval to Polygon format
        interval_map = {
            '1m': (1, 'minute'), '5m': (5, 'minute'), '15m': (15, 'minute'),
            '30m': (30, 'minute'), '1h': (1, 'hour'), '4h': (4, 'hour'),
            '1d': (1, 'day'), '1w': (1, 'week'), '1M': (1, 'month')
        }
        
        if interval not in interval_map:
            raise DataSourceError(f"Unsupported interval for Polygon: {interval}")
        
        multiplier, timespan = interval_map[interval]
        
        # Fetch aggregates
        aggs = client.get_aggs(
            ticker=ticker,
            multiplier=multiplier,
            timespan=timespan,
            from_=start_date,
            to=end_date
        )
        
        if not aggs:
            return pd.DataFrame()
        
        # Convert to DataFrame
        data = []
        for agg in aggs:
            data.append({
                'Open': agg.open,
                'High': agg.high,
                'Low': agg.low,
                'Close': agg.close,
                'Volume': agg.volume,
                'timestamp': pd.to_datetime(agg.timestamp, unit='ms')
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df
        
    except ImportError:
        raise DataSourceError("polygon-api-client package not installed. Install with: pip install polygon-api-client")
    except Exception as e:
        logger.error(f"Error fetching from Polygon: {e}")
        return pd.DataFrame()


def fetch_from_alphavantage(ticker: str, start_date: str, end_date: str, interval: str) -> pd.DataFrame:
    """
    Fetch data using Alpha Vantage API.
    
    Note: Alpha Vantage requires API key and has rate limits.
    
    Args:
        ticker: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval
    
    Returns:
        DataFrame with OHLCV data
    """
    api_key = os.environ.get('ALPHAVANTAGE_API_KEY', ALPHAVANTAGE_API_KEY)
    
    if not api_key:
        raise DataSourceError("Alpha Vantage API key not configured")
    
    try:
        import requests
        from datetime import datetime
        
        # Convert interval to Alpha Vantage format
        interval_map = {
            '1m': '1min', '5m': '5min', '15m': '15min',
            '30m': '30min', '1h': '60min', '1d': 'daily'
        }
        
        av_interval = interval_map.get(interval)
        if not av_interval:
            raise DataSourceError(f"Unsupported interval for Alpha Vantage: {interval}")
        
        # Determine function based on interval
        if interval == '1d':
            function = 'TIME_SERIES_DAILY'
        else:
            function = 'TIME_SERIES_INTRADAY'
        
        # Build URL
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': function,
            'symbol': ticker,
            'apikey': api_key,
            'outputsize': 'full'
        }
        
        if function == 'TIME_SERIES_INTRADAY':
            params['interval'] = av_interval
        
        # Fetch data
        response = requests.get(url, params=params)
        data = response.json()
        
        # Find the time series key
        ts_key = None
        for key in data.keys():
            if 'Time Series' in key:
                ts_key = key
                break
        
        if not ts_key or ts_key not in data:
            logger.error(f"No data returned from Alpha Vantage: {data}")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df_data = []
        for timestamp, values in data[ts_key].items():
            df_data.append({
                'timestamp': pd.to_datetime(timestamp),
                'Open': float(values['1. open']),
                'High': float(values['2. high']),
                'Low': float(values['3. low']),
                'Close': float(values['4. close']),
                'Volume': int(values['5. volume'])
            })
        
        df = pd.DataFrame(df_data)
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
        
        # Filter by date range
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        df = df[(df.index >= start_dt) & (df.index <= end_dt)]
        
        return df
        
    except Exception as e:
        logger.error(f"Error fetching from Alpha Vantage: {e}")
        return pd.DataFrame()


def fetch_ohlcv_multi_source(
    ticker: str,
    start_date: str,
    end_date: str,
    interval: str,
    source: Optional[str] = None
) -> pd.DataFrame:
    """
    Fetch OHLCV data from the configured data source with fallback support.
    
    Args:
        ticker: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        interval: Data interval (e.g., '5m', '15m', '1h', '1d')
        source: Optional data source override (default uses PRIMARY_DATA_SOURCE)
    
    Returns:
        DataFrame with OHLCV data
    """
    data_source = source or PRIMARY_DATA_SOURCE
    
    logger.info(f"Fetching {ticker} data from {data_source} ({start_date} to {end_date}, {interval})")
    
    # Map of available data sources
    source_map = {
        'yfinance': fetch_from_yfinance,
        'finnhub': fetch_from_finnhub,
        'polygon': fetch_from_polygon,
        'alphavantage': fetch_from_alphavantage
    }
    
    if data_source not in source_map:
        logger.warning(f"Unknown data source: {data_source}, falling back to yfinance")
        data_source = 'yfinance'
    
    try:
        # Try primary source
        fetch_func = source_map[data_source]
        data = fetch_func(ticker, start_date, end_date, interval)
        
        if not data.empty:
            logger.info(f"Successfully fetched {len(data)} records from {data_source}")
            return data
        
        # If primary source fails, fallback to yfinance
        if data_source != 'yfinance':
            logger.warning(f"No data from {data_source}, falling back to yfinance")
            data = fetch_from_yfinance(ticker, start_date, end_date, interval)
            
            if not data.empty:
                logger.info(f"Successfully fetched {len(data)} records from yfinance (fallback)")
                return data
        
        logger.warning(f"No data available for {ticker}")
        return pd.DataFrame()
        
    except DataSourceError as e:
        logger.error(f"Data source error: {e}")
        # Fallback to yfinance
        if data_source != 'yfinance':
            logger.info("Falling back to yfinance")
            return fetch_from_yfinance(ticker, start_date, end_date, interval)
        return pd.DataFrame()
    
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return pd.DataFrame()


if __name__ == '__main__':
    # Test the multi-source data fetching
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    ticker = 'AAPL'
    start_date = '2024-01-01'
    end_date = '2024-01-10'
    interval = '1d'
    
    print(f"\nTesting data fetch for {ticker}")
    print(f"Period: {start_date} to {end_date}")
    print(f"Interval: {interval}")
    print(f"Primary source: {PRIMARY_DATA_SOURCE}\n")
    
    data = fetch_ohlcv_multi_source(ticker, start_date, end_date, interval)
    
    if not data.empty:
        print("Data fetched successfully!")
        print(f"\nShape: {data.shape}")
        print("\nFirst few rows:")
        print(data.head())
        print("\nLast few rows:")
        print(data.tail())
    else:
        print("Failed to fetch data")
