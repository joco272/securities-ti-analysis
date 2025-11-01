import streamlit as st
import pandas as pd
import sys
import os

# Ensure the src directory is in the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_processing.data_retrieval import fetch_ohlcv
from src.data_processing.indicators import calculate_indicators
from src.data_processing.data_storage import write_indicators_to_db
from src.data_processing.data_query import fetch_data_with_indicators
from src.ml_models.backtesting_framework import run_backtest as run_vbt_backtest
from src.database import initialize_database
from src.portfolio import watchlist as wl
from src.portfolio import transaction as trans
from src.portfolio import summary as port
from src.plotting.charts import create_multi_pane_chart
from src.ml_models.feature_engineering import prepare_data_for_ml
from src.ml_models.model import train_and_save_model, load_model


def generate_rsi_signals(df):
    """Generates entry and exit signals based on a simple RSI strategy."""
    rsi = df['rsi']
    entry_signals = (rsi < 30).shift(1, fill_value=False)
    exit_signals = (rsi > 70).shift(1, fill_value=False)
    return entry_signals, exit_signals

def generate_ml_signals(model, df):
    """Generates entry and exit signals using a trained ML model."""
    feature_cols = model.feature_names_in_
    features_present = [col for col in feature_cols if col in df.columns]
    X = df[features_present]

    X.dropna(inplace=True)
    if X.empty:
        return pd.Series(dtype=bool), pd.Series(dtype=bool)

    predictions = model.predict(X)
    signals = pd.Series(predictions, index=X.index)

    entry_signals = (signals == 1)
    exit_signals = (signals == -1)
    return entry_signals, exit_signals


def main():
    st.title("Securities Analysis and Backtesting App")
    initialize_database()

    # --- Main Area ---
    st.header("My Portfolio")
    portfolio_summary = port.get_portfolio_summary()
    if not portfolio_summary:
        st.info("Your portfolio is empty.")
    else:
        portfolio_df = pd.DataFrame(portfolio_summary)
        # Formatting for display
        for col in ['average_cost', 'current_price', 'market_value', 'unrealized_pl']:
            portfolio_df[col] = portfolio_df[col].map('${:,.2f}'.format)
        st.dataframe(portfolio_df)

    # --- Sidebar ---
    st.sidebar.header("Analysis Parameters")
    ticker_input = st.sidebar.text_input("Enter a stock ticker (e.g., AAPL):", "AAPL")
    interval = st.sidebar.selectbox("Select interval:", ('1d', '1h', '15m'), index=0)
    start_date = st.sidebar.date_input("Start date", pd.to_datetime("2023-01-01"))
    end_date = st.sidebar.date_input("End date", pd.to_datetime("2023-12-31"))

    available_indicators = ["MACD", "RSI", "MFI", "Stochastic RSI", "OBV", "A/D", "Awesome Oscillator"]
    selected_indicators = st.sidebar.multiselect("Select indicators:", available_indicators, default=["MACD", "RSI"])

    if st.sidebar.button("Fetch, Store, and Analyze"):
        run_analysis(ticker_input, interval, start_date, end_date, selected_indicators)

    # --- ML Section ---
    st.sidebar.markdown("---")
    st.sidebar.header("Machine Learning")
    if st.sidebar.button("Train Model"):
        run_model_training(ticker_input, interval)
    if st.sidebar.button("Run ML Backtest"):
        run_ml_backtest(ticker_input, interval)

    # --- Watchlist Section ---
    st.sidebar.markdown("---")
    st.sidebar.header("Portfolio Management")
    new_watchlist_name = st.sidebar.text_input("Create New Watchlist:")
    if st.sidebar.button("Add Watchlist"):
        if new_watchlist_name:
            wl.add_watchlist(new_watchlist_name)
            st.sidebar.success(f"Watchlist '{new_watchlist_name}' created.")
        else:
            st.sidebar.warning("Please enter a name.")

    st.markdown("---")
    st.header("Watchlists")
    all_watchlists = wl.get_watchlists()
    if not all_watchlists:
        st.info("No watchlists created yet.")
    else:
        watchlist_names = {w['name']: w['id'] for w in all_watchlists}
        selected_name = st.selectbox("Select a watchlist:", list(watchlist_names.keys()))
        if selected_name:
            selected_id = watchlist_names[selected_name]
            st.subheader(f"Items in '{selected_name}'")
            items = wl.get_watchlist_items(selected_id)
            # (UI for adding/removing tickers)

    # --- Transaction Log Section ---
    st.markdown("---")
    st.header("Transaction Log")
    # (UI for adding/viewing transactions)


def run_analysis(ticker, interval, start_date, end_date, selected_indicators):
    with st.spinner("Processing..."):
        st.write("Fetching fresh data...")
        ohlcv_data = fetch_ohlcv(ticker, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), interval)
        if ohlcv_data.empty:
            st.warning("No new data found.")
            return

        st.write("Calculating indicators...")
        data_with_indicators = calculate_indicators(ohlcv_data)

        st.write("Storing data...")
        write_indicators_to_db(ticker, interval, data_with_indicators)
        st.success("Data processed and stored.")

        st.write("Querying data for display...")
        display_df = fetch_data_with_indicators(ticker, interval)
        if display_df.empty:
            st.warning("No data found in database.")
            return

        st.subheader(f"Analysis for {ticker}")
        fig = create_multi_pane_chart(display_df, selected_indicators)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Backtesting Results (RSI Strategy)")
        entry, exit_ = generate_rsi_signals(display_df)
        stats, plot = run_vbt_backtest(display_df, entry, exit_)
        st.write(pd.Series(stats, name="Performance"))
        st.plotly_chart(plot)

def run_model_training(ticker, interval):
    st.header("Model Training")
    with st.spinner("Preparing data for training..."):
        data = fetch_data_with_indicators(ticker, interval)
        if data.empty:
            st.warning("No data available to train the model.")
            return

        features, target = prepare_data_for_ml(data)
        if features.empty:
            st.warning("Not enough data to create features for the model.")
            return

    with st.spinner(f"Training model for {ticker}..."):
        model_path = f"models/{ticker}_{interval}_model.joblib"
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        train_and_save_model(features, target, model_path)
        st.success(f"Model for {ticker} ({interval}) trained and saved.")

def run_ml_backtest(ticker, interval):
    st.header("ML Backtest Results")
    model_path = f"models/{ticker}_{interval}_model.joblib"
    model = load_model(model_path)
    if model is None:
        st.warning("No trained model found. Please train the model first.")
        return

    with st.spinner("Running ML backtest..."):
        df = fetch_data_with_indicators(ticker, interval)
        if df.empty:
            st.warning("No data for backtest.")
            return

        entry, exit = generate_ml_signals(model, df)
        stats, plot = run_vbt_backtest(df, entry, exit)
        st.write(stats)
        st.plotly_chart(plot)

if __name__ == "__main__":
    main()
