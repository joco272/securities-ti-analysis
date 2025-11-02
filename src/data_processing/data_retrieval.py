import yfinance as yf
import pandas as pd

def fetch_ohlcv(ticker: str, start_date: str, end_date: str, interval: str) -> pd.DataFrame:
    """
    Fetches OHLCV data for a given ticker and date range.

    Args:
        ticker: The stock ticker symbol.
        start_date: The start date in YYYY-MM-DD format.
        end_date: The end date in YYYY-MM-DD format.
        interval: The data interval (e.g., '15m', '45m', '4h').

    Returns:
        A pandas DataFrame with the OHLCV data.
    """
    data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)
    return data

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
