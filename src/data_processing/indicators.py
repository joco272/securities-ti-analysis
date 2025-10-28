import pandas as pd
import talib
import numpy as np

def calculate_indicators(ohlcv_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates technical indicators and appends them to the DataFrame.

    Args:
        ohlcv_df: A pandas DataFrame with OHLCV data.

    Returns:
        The DataFrame with the calculated indicators.
    """
    df = ohlcv_df.copy()

    # Extract numpy arrays for talib and ensure they are of type double
    close = df['Close'].values.astype(np.double)
    high = df['High'].values.astype(np.double)
    low = df['Low'].values.astype(np.double)
    volume = df['Volume'].values.astype(np.double)

    # Calculate MACD
    macd, macdsignal, macdhist = talib.MACD(close)
    df['macd'] = macd
    df['macdsignal'] = macdsignal
    df['macdhist'] = macdhist

    # Calculate MFI
    df['mfi'] = talib.MFI(high, low, close, volume)

    # Calculate RSI
    df['rsi'] = talib.RSI(close)

    return df

if __name__ == '__main__':
    # This block is for testing purposes and will be removed later.
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from data_retrieval import fetch_ohlcv

    # Example usage with real data
    ticker = 'AAPL'
    start_date = '2023-01-01'
    end_date = '2023-12-31'
    interval = '1d'

    try:
        ohlcv_data = fetch_ohlcv(ticker, start_date, end_date, interval)
        if not ohlcv_data.empty:
            indicators_df = calculate_indicators(ohlcv_data)
            print("Successfully calculated indicators:")
            print(indicators_df.tail())
        else:
            print(f"No data found for {ticker} in the specified date range.")
    except Exception as e:
        print(f"An error occurred: {e}")
