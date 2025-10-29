import pandas as pd
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

def fetch_data_with_indicators(ticker: str, interval: str) -> pd.DataFrame:
    """
    Fetches price data and its associated indicators from the database,
    and reconstructs it into a single wide DataFrame.

    Args:
        ticker: The stock ticker symbol.
        interval: The data interval (e.g., '15m', '1d').

    Returns:
        A pandas DataFrame with OHLCV data and columns for each indicator value.
    """
    conn = get_db_connection()

    # SQL query to join the two tables
    query = """
    SELECT
        pd.timestamp,
        pd.open,
        pd.high,
        pd.low,
        pd.close,
        pd.volume,
        id.name AS indicator_name,
        id.values_json AS indicator_values
    FROM price_data pd
    LEFT JOIN indicator_data id ON pd.id = id.price_id
    WHERE pd.ticker = ? AND pd.interval = ?
    ORDER BY pd.timestamp;
    """

    df = pd.read_sql_query(query, conn, params=(ticker, interval))
    conn.close()

    if df.empty:
        return pd.DataFrame()

    # Pivot the table to create a "wide" format
    # The index will be the timestamp, and columns will be the base OHLCV fields plus each indicator
    pivot_df = df.pivot_table(
        index='timestamp',
        columns='indicator_name',
        values='indicator_values',
        aggfunc='first'
    ).reset_index()

    # Merge the pivoted indicator data back with the OHLCV data
    ohlcv_df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].drop_duplicates().set_index('timestamp')
    final_df = ohlcv_df.join(pivot_df.set_index('timestamp'))

    # Parse the JSON strings and expand them into separate columns
    json_cols = [col for col in final_df.columns if col not in ['open', 'high', 'low', 'close', 'volume']]

    for col_name in json_cols:
        # 1. Parse the JSON strings from the column into a temporary DataFrame
        parsed_data = final_df[col_name].apply(lambda x: json.loads(x) if pd.notna(x) else {})
        expanded_df = pd.json_normalize(parsed_data)

        # 2. Rename the new columns to avoid collisions (e.g., 'value' becomes 'rsi', 'macd' becomes 'macd_macd')
        expanded_df.rename(columns=lambda x: f"{col_name}_{x}" if x != 'value' else col_name, inplace=True)
        expanded_df.index = final_df.index

        # 3. Drop the original JSON column from the main DataFrame
        final_df.drop(columns=[col_name], inplace=True)

        # 4. Join the new, expanded columns
        final_df = final_df.join(expanded_df)

    # Convert timestamp index back to Datetime object for compatibility with backtesting library
    final_df.index = pd.to_datetime(final_df.index)

    # Rename columns to match what the rest of the app expects (e.g., 'macd_macd' to 'macd')
    final_df.rename(columns={'macd_macd': 'macd', 'macd_signal': 'macdsignal', 'macd_hist': 'macdhist'}, inplace=True)

    # Ensure OHLCV columns are of the correct type
    for col in ['open', 'high', 'low', 'close', 'volume']:
        final_df[col] = pd.to_numeric(final_df[col], errors='coerce')

    return final_df

if __name__ == '__main__':
    # This block is for testing purposes.
    ticker = 'MSFT'
    interval = '1d'

    try:
        reconstructed_df = fetch_data_with_indicators(ticker, interval)
        if not reconstructed_df.empty:
            print(f"Successfully fetched and reconstructed data for {ticker}.")
            print("Columns:", reconstructed_df.columns)
            print(reconstructed_df.tail())
        else:
            print(f"No data found for {ticker} in the database.")
    except Exception as e:
        print(f"An error occurred: {e}")
