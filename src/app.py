import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processing.data_retrieval import fetch_ohlcv
from data_processing.indicators import calculate_indicators
from data_processing.data_storage import write_indicators_to_db
from ml_models.backtesting_framework import run_backtest

def main():
    """
    The main function for the Streamlit application.
    """
    st.title("Securities Analysis and Backtesting App")

    # --- User Input ---
    ticker = st.text_input("Enter a stock ticker (e.g., AAPL):", "AAPL")
    interval = st.selectbox("Select interval:", ('15m', '1h', '4h', '1d'), index=3)
    start_date = st.date_input("Start date", pd.to_datetime("2023-10-01"))
    end_date = st.date_input("End date", pd.to_datetime("2023-12-31"))

    if st.button("Run Analysis"):
        with st.spinner("Fetching data and running analysis..."):
            try:
                # --- 1. Fetch Data ---
                ohlcv_data = fetch_ohlcv(ticker, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), interval)
                if ohlcv_data.empty:
                    st.warning(f"No data found for {ticker}.")
                    return

                # --- 2. Calculate Indicators ---
                data_with_indicators = calculate_indicators(ohlcv_data)

                # --- 3. Store Indicators ---
                write_indicators_to_db(ticker, interval, data_with_indicators.dropna())
                st.success(f"Successfully stored {len(data_with_indicators.dropna())} data points in the local SQLite database.")

                # --- 4. Display Data and Indicators ---
                st.subheader(f"{ticker} Price and Technical Indicators ({interval})")
                st.line_chart(data_with_indicators[['Close', 'rsi', 'mfi']])
                st.dataframe(data_with_indicators.tail())

                # --- 4. Run Backtest ---
                st.subheader("Backtesting Results")

                results = run_backtest(data_with_indicators.dropna())

                # --- 5. Display Backtest Results ---
                st.write(f"Sharpe Ratio: {results['Sharpe Ratio']:.2f}")
                st.write(f"Win Rate [%]: {results['Win Rate [%]']:.2f}")

            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
