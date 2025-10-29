import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

def write_indicators_to_db(ticker: str, interval: str, data: pd.DataFrame):
    """
    Writes the indicator data to the SQLite database.

    Args:
        ticker: The stock ticker symbol.
        interval: The data interval (e.g., '15m', '4h', '1d').
        data: A pandas DataFrame with the indicator data.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    for timestamp, row in data.iterrows():
        cursor.execute("""
        INSERT OR REPLACE INTO indicators (timestamp, ticker, interval, open, high, low, close, volume, macd, macdsignal, macdhist, mfi, rsi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(timestamp), ticker, interval,
            row["Open"], row["High"], row["Low"], row["Close"], row["Volume"],
            row["macd"], row["macdsignal"], row["macdhist"], row["mfi"], row["rsi"]
        ))

    conn.commit()
    conn.close()
    print(f"Successfully wrote {len(data)} data points to the database for {ticker} at {interval} interval.")

if __name__ == '__main__':
    # This block is for testing purposes and will be removed later.
    from data_retrieval import fetch_ohlcv
    from indicators import calculate_indicators

    ticker = 'AAPL'
    start_date = '2023-01-01'
    end_date = '2023-12-31'
    interval = '1d'

    try:
        ohlcv_data = fetch_ohlcv(ticker, start_date, end_date, interval)
        if not ohlcv_data.empty:
            indicators_df = calculate_indicators(ohlcv_data).dropna()
            write_indicators_to_db(ticker, interval, indicators_df)
        else:
            print(f"No data found for {ticker} in the specified date range.")
    except Exception as e:
        print(f"An error occurred: {e}")
