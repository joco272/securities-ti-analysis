import pandas as pd
import talib
import pandas_ta as ta
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

    # --- TA-Lib Indicators ---
    # Ensure data is in the correct format for TA-Lib
    close = df['close'].values.astype(np.double)
    high = df['high'].values.astype(np.double)
    low = df['low'].values.astype(np.double)
    volume = df['volume'].values.astype(np.double)

    # MACD
    macd, macdsignal, macdhist = talib.MACD(close)
    df['macd'] = macd
    df['macdsignal'] = macdsignal
    df['macdhist'] = macdhist

    # MFI
    df['mfi'] = talib.MFI(high, low, close, volume)

    # RSI
    df['rsi'] = talib.RSI(close)

    # Stochastic RSI
    stoch_rsi_k, stoch_rsi_d = talib.STOCHRSI(close)
    df['stoch_rsi_k'] = stoch_rsi_k
    df['stoch_rsi_d'] = stoch_rsi_d

    # Accumulation/Distribution Line (A/D)
    df['ad'] = talib.AD(high, low, close, volume)

    # On-Balance Volume (OBV)
    df['obv'] = talib.OBV(close, volume)

    # Simple Moving Averages
    df['sma50'] = talib.SMA(close, timeperiod=50)
    df['sma200'] = talib.SMA(close, timeperiod=200)

    # --- Pandas TA Indicators ---
    # The pandas-ta library can directly work with the DataFrame
    df.ta.ao(append=True)
    # The column name will be 'AO_5_34', let's rename it for simplicity
    if 'AO_5_34' in df.columns:
        df.rename(columns={'AO_5_34': 'ao'}, inplace=True)

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
