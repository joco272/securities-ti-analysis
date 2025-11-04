import pandas as pd
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

def write_indicators_to_db(ticker: str, interval: str, data: pd.DataFrame):
    """
    Writes price and indicator data to the new two-table SQLite database schema.

    Args:
        ticker: The stock ticker symbol.
        interval: The data interval (e.g., '15m', '1d').
        data: A pandas DataFrame with OHLCV and calculated indicator data.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    for timestamp, row in data.iterrows():
        # Step 1: Insert price data and get the ID.
        # 'INSERT OR IGNORE' prevents duplicates based on the UNIQUE constraint.
        cursor.execute("""
        INSERT OR IGNORE INTO price_data (timestamp, ticker, interval, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (str(timestamp), ticker, interval, row["Open"], row["High"], row["Low"], row["Close"], row["Volume"]))

        # Fetch the ID of the price data, whether it was just inserted or already existed.
        cursor.execute("SELECT id FROM price_data WHERE timestamp=? AND ticker=? AND interval=?", (str(timestamp), ticker, interval))
        price_id_result = cursor.fetchone()
        if price_id_result is None:
            continue  # Should not happen in normal flow
        price_id = price_id_result[0]

        # Step 2: Prepare indicator data as JSON and insert into indicator_data table.
        # Initial indicators as per PRD: MACD, MFI, RSI
        indicators = {
            "macd": {"macd": row.get("macd"), "signal": row.get("macdsignal"), "hist": row.get("macdhist")},
            "mfi": {"value": row.get("mfi")},
            "rsi": {"value": row.get("rsi")}
        }

        for name, values in indicators.items():
            # Skip if all values for an indicator are NaN (which happens at the start of the dataset)
            if all(pd.isna(v) for v in values.values()):
                continue

            values_json = json.dumps(values)
            cursor.execute("""
            INSERT OR IGNORE INTO indicator_data (price_id, name, values_json)
            VALUES (?, ?, ?)
            """, (price_id, name, values_json))

    conn.commit()
    conn.close()
    print(f"Successfully processed {len(data)} data points for {ticker} at {interval} interval.")

if __name__ == '__main__':
    # This block is for testing purposes.
    from data_processing.data_retrieval import fetch_ohlcv
    from data_processing.indicators import calculate_indicators

    ticker = 'MSFT'
    start_date = '2023-01-01'
    end_date = '2023-12-31'
    interval = '1d'

    try:
        ohlcv_data = fetch_ohlcv(ticker, start_date, end_date, interval)
        if not ohlcv_data.empty:
            indicators_df = calculate_indicators(ohlcv_data)
            write_indicators_to_db(ticker, interval, indicators_df)
        else:
            print(f"No data found for {ticker} in the specified date range.")
    except Exception as e:
        print(f"An error occurred: {e}")
