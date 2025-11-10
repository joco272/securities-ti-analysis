import pandas as pd
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

def fetch_data_with_indicators(ticker: str, interval: str) -> pd.DataFrame:
    """
    Fetches price data and its associated indicators from the database,
    and reconstructs it into a single wide DataFrame efficiently.

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

    # 1. Create the base OHLCV DataFrame
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    ohlcv_df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].drop_duplicates().set_index('timestamp')

    # 2. Process each indicator separately and efficiently
    indicator_dfs = []
    # Drop rows where indicator_name is null (from LEFT JOIN with no match)
    df.dropna(subset=['indicator_name', 'indicator_values'], inplace=True)

    unique_indicator_names = df['indicator_name'].unique()

    for name in unique_indicator_names:
        # Filter for the current indicator
        indicator_subset = df[df['indicator_name'] == name][['timestamp', 'indicator_values']].set_index('timestamp')

        # Parse JSON and normalize
        parsed_data = indicator_subset['indicator_values'].apply(json.loads)
        expanded_df = pd.json_normalize(parsed_data)
        expanded_df.index = indicator_subset.index

        # Rename columns to avoid collisions
        expanded_df.rename(columns=lambda x: f"{name}_{x}" if x != 'value' else name, inplace=True)
        indicator_dfs.append(expanded_df)

    # 3. Join the base OHLCV data with all expanded indicator dataframes
    final_df = ohlcv_df
    if indicator_dfs:
        all_indicators_df = pd.concat(indicator_dfs, axis=1)
        # Remove duplicate columns that might arise
        all_indicators_df = all_indicators_df.loc[:,~all_indicators_df.columns.duplicated()]
        final_df = final_df.join(all_indicators_df, how='left')

    # 4. Final column renaming and type conversion
    final_df.rename(columns={
        'macd_macd': 'macd',
        'macd_signal': 'macdsignal',
        'macd_hist': 'macdhist',
        'stoch_rsi_k': 'stoch_rsi_k',
        'stoch_rsi_d': 'stoch_rsi_d',
        'sma_sma50': 'sma50',
        'sma_sma200': 'sma200',
        'ao': 'ao'
    }, inplace=True, errors='ignore')

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
