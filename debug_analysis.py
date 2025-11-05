
import sys
import os
import pandas as pd
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_processing.data_retrieval import fetch_ohlcv
from src.data_processing.indicators import calculate_indicators
from src.data_processing.data_storage import write_indicators_to_db
from src.data_processing.data_query import fetch_data_with_indicators
from src.plotting.charts import create_multi_pane_chart

def run_analysis_local(ticker, interval, start_date, end_date, selected_indicators, chart_colors):
    """
    A local version of the run_analysis function from app.py for debugging.
    """
    try:
        print("--- 1. Fetching fresh data from yfinance ---")
        ohlcv_data = fetch_ohlcv(ticker, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), interval)
        if ohlcv_data.empty:
            print(f"No new data found for {ticker}.")
            return

        print("--- 2. Calculating Indicators ---")
        data_with_indicators = calculate_indicators(ohlcv_data)

        print("--- 3. Storing Price and Indicators in DB ---")
        write_indicators_to_db(ticker, interval, data_with_indicators)

        print("--- 4. Querying and Reconstructing Data from DB ---")
        display_df = fetch_data_with_indicators(ticker, interval)

        if display_df.empty:
            print("No data found in the database for the selected parameters.")
            return

        print("--- 5. Creating Chart ---")
        fig = create_multi_pane_chart(display_df, selected_indicators, chart_colors)

        print("Analysis complete!")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Default parameters from the Streamlit app
    ticker_input = "AAPL"
    interval = "1d"
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2023, 12, 31)
    selected_indicators = ["MACD", "RSI"]
    chart_colors = {
        'background': '#ffffff',
        'bullish_candle': '#26a69a',
        'bearish_candle': '#ef5350',
        'macd_line': '#009688',
        'macdsignal_line': '#ff5722',
        'macdhist': '#607d8b'
    }

    run_analysis_local(ticker_input, interval, start_date, end_date, selected_indicators, chart_colors)
