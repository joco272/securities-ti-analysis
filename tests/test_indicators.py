import sys
import os

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_processing.data_retrieval import fetch_ohlcv
from src.data_processing.indicators import calculate_indicators

if __name__ == '__main__':
    # This block is for testing purposes.
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
