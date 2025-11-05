import streamlit as st
import pandas as pd
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processing.data_retrieval import fetch_ohlcv
from data_processing.indicators import calculate_indicators
from data_processing.data_storage import write_indicators_to_db
from data_processing.data_query import fetch_data_with_indicators
from ml_models.backtesting_framework import run_backtest
from database import initialize_database
from portfolio import watchlist as wl
from portfolio import transaction as trans
from portfolio import summary as port
from plotting.charts import create_multi_pane_chart

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

    # --- Backtesting Parameters ---
    st.sidebar.header("Backtesting Parameters")
    strategy_indicator = st.sidebar.selectbox("Select a strategy:", ["RSI", "MFI", "Stochastic RSI", "MACD"])

    # Set default values based on the selected strategy
    if strategy_indicator == "RSI":
        defaults = (30, 70)
    elif strategy_indicator in ["MFI", "Stochastic RSI"]:
        defaults = (20, 80)
    else: # MACD
        defaults = (0, 0) # Not used for MACD

    if strategy_indicator == "MACD":
        macd_strategy = st.sidebar.selectbox("MACD Strategy Type:", ["Crossover", "Level"])
        if macd_strategy == "Level":
            macd_level = st.sidebar.number_input("MACD Level", value=0.0)
        lower_bound = upper_bound = macd_level if macd_strategy == "Level" else 0
    else:
        lower_bound = st.sidebar.slider("Lower Bound", 0, 100, defaults[0])
        upper_bound = st.sidebar.slider("Upper Bound", 0, 100, defaults[1])
        macd_strategy = None

    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Fetch, Store, and Analyze"):
            display_df, fig = run_analysis(ticker_input, interval, start_date, end_date, selected_indicators, strategy_indicator, lower_bound, upper_bound, macd_strategy)
            if display_df is not None and fig is not None:
                st.session_state.display_df = display_df
                st.session_state.fig = fig
    with col2:
        if st.button("Perform Backtest"):
            results = perform_backtest(ticker_input, interval, strategy_indicator, lower_bound, upper_bound, macd_strategy)
            if results is not None:
                st.session_state.results = results

    if 'display_df' in st.session_state and 'fig' in st.session_state:
        st.subheader(f"Displaying Data for {ticker_input} ({interval})")
        st.plotly_chart(st.session_state.fig, use_container_width=True)
        st.subheader("Latest Data and Indicators")
        st.dataframe(st.session_state.display_df.tail())

    if 'results' in st.session_state:
        st.subheader("Backtesting Results")
        st.write(f"Sharpe Ratio: {st.session_state.results['Sharpe Ratio']:.2f}")
        st.write(f"Win Rate [%]: {st.session_state.results['Win Rate [%]']:.2f}")

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


def run_analysis(ticker, interval, start_date, end_date, selected_indicators, strategy_indicator, lower_bound, upper_bound, macd_strategy):
    try:
        with st.spinner("Processing..."):
            # --- 1. Fetch fresh data from yfinance ---
            ohlcv_data = fetch_ohlcv(ticker, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), interval)
            if ohlcv_data.empty:
                st.warning(f"No new data found for {ticker}.")
                return None, None

            # --- 2. Calculate Indicators ---
            data_with_indicators = calculate_indicators(ohlcv_data)

            # --- 3. Store Price and Indicators in DB ---
            write_indicators_to_db(ticker, interval, data_with_indicators)

            # --- 4. Query and Reconstruct Data from DB ---
            display_df = fetch_data_with_indicators(ticker, interval)

        if display_df.empty:
            st.warning("No data found in the database for the selected parameters.")
            return None, None

        # --- 5. Create Chart ---
        fig = create_multi_pane_chart(display_df, selected_indicators)

        st.success("Analysis complete!")

        return display_df, fig

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None, None

def perform_backtest(ticker, interval, strategy_indicator, lower_bound, upper_bound, macd_strategy):
    try:
        with st.spinner("Performing backtest..."):
            display_df = fetch_data_with_indicators(ticker, interval)
            if display_df.empty:
                st.warning("No data found for backtesting. Please run the analysis first.")
                return None

            # Map strategy name to indicator column
            indicator_map = {
                "RSI": "rsi",
                "MFI": "mfi",
                "Stochastic RSI": "stoch_rsi_k", # Using the %K line
                "MACD": "MACD" # Special case for MACD
            }
            indicator_to_backtest = indicator_map.get(strategy_indicator)

            results = run_backtest(display_df.dropna(), indicator_to_backtest, lower_bound, upper_bound, macd_strategy)

            st.success("Backtest complete!")

            return results

    except Exception as e:
        st.error(f"An error occurred during backtesting: {e}")
        return None

if __name__ == "__main__":
    main()
