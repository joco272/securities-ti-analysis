import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processing.data_retrieval import fetch_ohlcv
from data_processing.indicators import calculate_indicators
from data_processing.data_storage import write_indicators_to_db
from data_processing.data_query import fetch_data_with_indicators
from ml_models.backtesting_framework import run_backtest
from database import initialize_database

def main():
    """
    The main function for the Streamlit application.
    """
    st.title("Securities Analysis and Backtesting App")

    # Initialize the database on first run
    initialize_database()

    # --- User Input ---
    st.sidebar.header("User Input")
    ticker = st.sidebar.text_input("Enter a stock ticker (e.g., AAPL):", "AAPL")
    interval = st.sidebar.selectbox("Select interval:", ('15m', '1h', '4h', '1d'), index=3)
    start_date = st.sidebar.date_input("Start date", pd.to_datetime("2023-01-01"))
    end_date = st.sidebar.date_input("End date", pd.to_datetime("2023-12-31"))

    if st.sidebar.button("Fetch, Store, and Analyze"):
        with st.spinner("Processing..."):
            try:
                # --- 1. Fetch fresh data from yfinance ---
                st.write(f"Fetching fresh data for {ticker}...")
                ohlcv_data = fetch_ohlcv(ticker, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), interval)
                if ohlcv_data.empty:
                    st.warning(f"No new data found for {ticker}.")
                    return

                # --- 2. Calculate Indicators ---
                st.write("Calculating technical indicators...")
                data_with_indicators = calculate_indicators(ohlcv_data)

                # --- 3. Store Price and Indicators in DB ---
                st.write("Storing data in the database...")
                write_indicators_to_db(ticker, interval, data_with_indicators)
                st.success(f"Successfully processed and stored data for {len(data_with_indicators)} records.")

                # --- 4. Query and Reconstruct Data from DB ---
                st.write("Querying data from the database for display...")
                display_df = fetch_data_with_indicators(ticker, interval)

                if display_df.empty:
                    st.warning("No data found in the database for the selected parameters.")
                    return

                # --- 5. Display Data and Indicators ---
                st.subheader(f"Displaying Data for {ticker} ({interval})")

                # Create a list of available indicator columns for the chart
                chart_cols = ['close', 'rsi', 'mfi', 'macd', 'macdsignal']
                available_chart_cols = [col for col in chart_cols if col in display_df.columns]
                st.line_chart(display_df[available_chart_cols])
                st.dataframe(display_df.tail())

                # --- 6. Run Backtest ---
                st.subheader("Backtesting Results")
                results = run_backtest(display_df.dropna())

                # --- 7. Display Backtest Results ---
                st.write(f"Sharpe Ratio: {results['Sharpe Ratio']:.2f}")
                st.write(f"Win Rate [%]: {results['Win Rate [%]']:.2f}")

            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
