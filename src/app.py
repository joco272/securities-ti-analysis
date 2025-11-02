import streamlit as st
import pandas as pd
import sys
import os

from data_processing.data_retrieval import fetch_ohlcv
from data_processing.indicators import calculate_indicators
from data_processing.data_storage import write_indicators_to_db
from data_processing.data_query import fetch_data_with_indicators
from database import initialize_database
from portfolio import watchlist as wl
from portfolio import transaction as trans
from portfolio import summary as port
from plotting.charts import create_multi_pane_chart
from ml_models.feature_engineering import prepare_data_for_ml
from ml_models.model import train_and_save_model, load_model
from ml_models.backtesting_framework import run_backtest as run_vbt_backtest


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

    # Ensure no NaN values are passed to the model
    X.dropna(inplace=True)
    if X.empty:
        return pd.Series(dtype=bool), pd.Series(dtype=bool)

    predictions = model.predict(X)
    signals = pd.Series(predictions, index=X.index)

    # Align signals with the original DataFrame index
    entry_signals = (signals == 1).reindex(df.index, fill_value=False)
    exit_signals = (signals == -1).reindex(df.index, fill_value=False)
    return entry_signals, exit_signals


def main():
    """
    The main function for the Streamlit application.
    """
    st.title("Securities Analysis and Backtesting App")

    # Initialize the database on first run
    initialize_database()

    # --- Main Area ---
    st.header("My Portfolio")
    portfolio_summary = port.get_portfolio_summary()

    if not portfolio_summary:
        st.info("Your portfolio is empty. Add transactions in the 'Transaction Log' section below to see your holdings.")
    else:
        # Convert to DataFrame for better display and formatting
        portfolio_df = pd.DataFrame(portfolio_summary)

        # Formatting the currency columns
        portfolio_df['average_cost'] = portfolio_df['average_cost'].map('${:,.2f}'.format)
        portfolio_df['current_price'] = portfolio_df['current_price'].map('${:,.2f}'.format)
        portfolio_df['market_value'] = portfolio_df['market_value'].map('${:,.2f}'.format)
        portfolio_df['unrealized_pl'] = portfolio_df['unrealized_pl'].map('${:,.2f}'.format)

        st.dataframe(portfolio_df)

    # --- Sidebar for User Input ---
    st.sidebar.header("Analysis Parameters")
    ticker_input = st.sidebar.text_input("Enter a stock ticker (e.g., AAPL):", "AAPL")
    interval = st.sidebar.selectbox("Select interval:", ('15m', '1h', '4h', '1d'), index=3)
    start_date = st.sidebar.date_input("Start date", pd.to_datetime("2023-01-01"))
    end_date = st.sidebar.date_input("End date", pd.to_datetime("2023-12-31"))

    # --- Indicator Selection ---
    available_indicators = ["MACD", "RSI", "MFI", "Stochastic RSI", "OBV", "A/D", "Awesome Oscillator"]
    selected_indicators = st.sidebar.multiselect("Select indicators to display:", available_indicators, default=["MACD", "RSI"])

    if st.sidebar.button("Fetch, Store, and Analyze"):
        run_analysis(ticker_input, interval, start_date, end_date, selected_indicators)

    # --- ML Section ---
    st.sidebar.markdown("---")
    st.sidebar.header("Machine Learning")
    if st.sidebar.button("Train Model"):
        run_model_training(ticker_input, interval)
    if st.sidebar.button("Run ML Backtest"):
        run_ml_backtest(ticker_input, interval)

    # --- Portfolio Management Section ---
    st.sidebar.markdown("---")
    st.sidebar.header("Portfolio Management")
    new_watchlist_name = st.sidebar.text_input("Create New Watchlist:")
    if st.sidebar.button("Add Watchlist"):
        if new_watchlist_name:
            wl.add_watchlist(new_watchlist_name)
            st.sidebar.success(f"Watchlist '{new_watchlist_name}' created.")
            # We don't need to manually refresh, Streamlit's state management will handle it
        else:
            st.sidebar.warning("Please enter a name for the new watchlist.")

    # --- Main Area for Watchlist Display ---
    st.markdown("---")
    st.header("Watchlists")

    all_watchlists = wl.get_watchlists()
    if not all_watchlists:
        st.info("No watchlists created yet. Use the sidebar to add one.")
    else:
        # Create a select box for all available watchlists
        watchlist_names = {w['name']: w['id'] for w in all_watchlists}
        selected_watchlist_name = st.selectbox("Select a watchlist to view:", list(watchlist_names.keys()))

        if selected_watchlist_name:
            selected_watchlist_id = watchlist_names[selected_watchlist_name]

            # --- Display and Manage Watchlist Items ---
            st.subheader(f"Items in '{selected_watchlist_name}'")
            watchlist_items = wl.get_watchlist_items(selected_watchlist_id)

            # Form to add a new ticker
            with st.form(key="add_ticker_form"):
                new_ticker = st.text_input("Add Ticker to this Watchlist (e.g., NVDA):")
                submit_button = st.form_submit_button("Add Ticker")
                if submit_button and new_ticker:
                    wl.add_to_watchlist(selected_watchlist_id, new_ticker)
                    st.success(f"Added {new_ticker} to '{selected_watchlist_name}'.")
                    # No need to refresh, Streamlit will re-run

            # Display existing items with a 'Remove' button for each
            if not watchlist_items:
                st.write("This watchlist is empty.")
            else:
                for item in watchlist_items:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(item['ticker'])
                    with col2:
                        # Use a unique key for each button
                        if st.button(f"Remove", key=f"remove_{item['id']}"):
                            wl.remove_from_watchlist(item['id'])
                            # No need to refresh
                            st.experimental_rerun() # Force an immediate rerun for snappier UI

    # --- Transaction Log Section ---
    st.markdown("---")
    st.header("Transaction Log")

    # Form to add a new transaction
    with st.expander("Add New Transaction"):
        with st.form(key="add_transaction_form"):
            trans_ticker = st.text_input("Ticker")
            trans_date = st.date_input("Transaction Date")
            trans_type = st.selectbox("Type", ["buy", "sell"])
            trans_quantity = st.number_input("Quantity", min_value=0.0, format="%.4f")
            trans_price = st.number_input("Price per Share", min_value=0.0, format="%.2f")

            submit_trans_button = st.form_submit_button("Add Transaction")
            if submit_trans_button:
                if all([trans_ticker, trans_date, trans_type, trans_quantity > 0, trans_price > 0]):
                    trans.add_transaction(trans_ticker, trans_date, trans_type, trans_quantity, trans_price)
                    st.success(f"Transaction for {trans_ticker} added.")
                else:
                    st.warning("Please fill out all fields with valid values.")

    # Display transactions for the ticker being analyzed
    st.subheader(f"History for {ticker_input}")
    transactions = trans.get_transactions(ticker_input)
    if not transactions:
        st.info(f"No transactions found for {ticker_input}.")
    else:
        # Create a DataFrame for better display
        trans_df = pd.DataFrame(transactions)
        st.dataframe(trans_df)


def run_analysis(ticker, interval, start_date, end_date, selected_indicators):
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

            # Create and display the advanced multi-pane chart
            fig = create_multi_pane_chart(display_df, selected_indicators)
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Latest Data and Indicators")
            st.dataframe(display_df.tail())

            # --- 6. Run Backtest (Simple RSI Strategy) ---
            st.subheader("Backtesting Results (RSI Strategy)")
            entry, exit_ = generate_rsi_signals(display_df)
            stats, plot = run_vbt_backtest(display_df, entry, exit_)

            # Display stats and plot
            st.write(pd.Series(stats, name="Performance"))
            st.plotly_chart(plot)

        except Exception as e:
            st.error(f"An error occurred during analysis: {e}")


def run_model_training(ticker, interval):
    """Handles the model training process."""
    st.header("Model Training")
    with st.spinner("Preparing data for training..."):
        data = fetch_data_with_indicators(ticker, interval)
        if data.empty:
            st.warning("No data available to train the model.")
            return

        features, target = prepare_data_for_ml(data)
        if features.empty or target.empty:
            st.warning("Not enough data to create features for the model.")
            return

    with st.spinner(f"Training model for {ticker}..."):
        # Define the path for the saved model
        model_path = f"models/{ticker}_{interval}_model.joblib"
        train_and_save_model(features, target, model_path)
        st.success(f"Model for {ticker} ({interval}) trained and saved successfully.")


def run_ml_backtest(ticker, interval):
    """Runs the backtest using the trained ML model."""
    st.header("ML Backtest Results")
    model_path = f"models/{ticker}_{interval}_model.joblib"

    # Load the model
    model = load_model(model_path)
    if model is None:
        st.warning("No trained model found. Please train the model first.")
        return

    with st.spinner("Running ML backtest..."):
        # Fetch the data needed for the backtest
        df = fetch_data_with_indicators(ticker, interval)
        if df.empty:
            st.warning("No data found to run the backtest.")
            return

        # Generate signals using the model
        entry, exit = generate_ml_signals(model, df)

        # Run the backtest
        stats, plot = run_vbt_backtest(df, entry, exit)

        # Display the results
        st.write("Performance Metrics:")
        st.write(pd.Series(stats, name="ML Strategy"))
        st.plotly_chart(plot)


if __name__ == "__main__":
    main()
