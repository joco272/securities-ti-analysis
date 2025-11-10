import streamlit as st
import pandas as pd
import sys
import os

from data_processing.data_retrieval import fetch_ohlcv
from data_processing.indicators import calculate_indicators
from data_processing.data_storage import write_indicators_to_db
from data_processing.data_query import fetch_data_with_indicators
from ml_models.backtesting_framework import run_backtest
from database import initialize_database
from portfolio import watchlist as wl
from portfolio import transaction as trans
from portfolio import summary as port
from portfolio import user_profile as up
from plotting.charts import create_multi_pane_chart

def main():
    """
    The main function for the Streamlit application.
    """
    st.title("Securities Analysis and Backtesting App")

    # Initialize the database on first run
    initialize_database()

    # --- Sidebar Navigation ---
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to:", ["Dashboard", "User Profile", "Watchlists", "Transaction Log"])

    if page == "Dashboard":
        render_dashboard()
    elif page == "User Profile":
        render_user_profile()
    elif page == "Watchlists":
        render_watchlists()
    elif page == "Transaction Log":
        render_transaction_log()

def render_dashboard():
    """
    Renders the main dashboard with portfolio summary and analysis tools.
    """
    # Get user profile for default values
    profile = up.get_user_profile()
    
    # --- Main Area ---
    st.header("My Portfolio")
    portfolio_summary = port.get_portfolio_summary()

    if not portfolio_summary:
        st.info("Your portfolio is empty. Add transactions in the 'Transaction Log' section to see your holdings.")
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
    
    # Use profile defaults
    default_ticker = profile.get('default_ticker', 'AAPL') if profile else 'AAPL'
    default_interval = profile.get('default_interval', '1d') if profile else '1d'
    
    ticker_input = st.sidebar.text_input("Enter a stock ticker (e.g., AAPL):", default_ticker)
    
    # Get the index of default interval
    intervals = ['15m', '1h', '4h', '1d']
    default_index = intervals.index(default_interval) if default_interval in intervals else 3
    
    interval = st.sidebar.selectbox("Select interval:", intervals, index=default_index)
    start_date = st.sidebar.date_input("Start date", pd.to_datetime("2023-01-01"))
    end_date = st.sidebar.date_input("End date", pd.to_datetime("2023-12-31"))

    # --- Indicator Selection ---
    available_indicators = ["MACD", "RSI", "MFI", "Stochastic RSI", "OBV", "A/D", "Awesome Oscillator"]
    selected_indicators = st.sidebar.multiselect("Select indicators to display:", available_indicators, default=["MACD", "RSI"])

    if st.sidebar.button("Fetch, Store, and Analyze"):
        # This block remains for the analysis part of the app
        run_analysis(ticker_input, interval, start_date, end_date, selected_indicators)

def render_user_profile():
    """
    Renders the user profile page for viewing and editing user settings.
    """
    st.header("User Profile")
    
    # Get current profile
    profile = up.get_user_profile()
    
    if not profile:
        st.warning("No profile found. Creating default profile...")
        profile = up.get_user_profile()
    
    st.write("Manage your personal settings and preferences.")
    
    # Profile edit form
    with st.form(key="profile_form"):
        st.subheader("Profile Settings")
        
        username = st.text_input("Username", value=profile.get('username', 'User'))
        email = st.text_input("Email", value=profile.get('email', ''))
        
        st.subheader("Trading Preferences")
        
        default_ticker = st.text_input(
            "Default Ticker", 
            value=profile.get('default_ticker', 'AAPL'),
            help="The default stock ticker to use when opening the app"
        )
        
        intervals = ['15m', '1h', '4h', '1d']
        current_interval = profile.get('default_interval', '1d')
        default_interval_index = intervals.index(current_interval) if current_interval in intervals else 3
        
        default_interval = st.selectbox(
            "Default Interval",
            intervals,
            index=default_interval_index,
            help="The default time interval for analysis"
        )
        
        risk_tolerances = ['Low', 'Medium', 'High']
        current_risk = profile.get('risk_tolerance', 'Medium')
        risk_index = risk_tolerances.index(current_risk) if current_risk in risk_tolerances else 1
        
        risk_tolerance = st.selectbox(
            "Risk Tolerance",
            risk_tolerances,
            index=risk_index,
            help="Your risk tolerance level for trading strategies"
        )
        
        submit_button = st.form_submit_button("Save Profile")
        
        if submit_button:
            try:
                up.update_user_profile(username, email, default_ticker, default_interval, risk_tolerance)
                st.success("Profile updated successfully!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error updating profile: {e}")
    
    # Display current profile summary
    st.markdown("---")
    st.subheader("Current Profile")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Username", profile.get('username', 'N/A'))
        st.metric("Default Ticker", profile.get('default_ticker', 'N/A'))
        st.metric("Risk Tolerance", profile.get('risk_tolerance', 'N/A'))
    
    with col2:
        st.metric("Email", profile.get('email', 'Not set') if profile.get('email') else 'Not set')
        st.metric("Default Interval", profile.get('default_interval', 'N/A'))

def render_watchlists():
    """
    Renders the watchlists page.
    """
    st.header("Watchlists")
    
    # --- Portfolio Management Section ---
    st.sidebar.header("Portfolio Management")
    new_watchlist_name = st.sidebar.text_input("Create New Watchlist:")
    if st.sidebar.button("Add Watchlist"):
        if new_watchlist_name:
            wl.add_watchlist(new_watchlist_name)
            st.sidebar.success(f"Watchlist '{new_watchlist_name}' created.")
        else:
            st.sidebar.warning("Please enter a name for the new watchlist.")

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
                            st.experimental_rerun()

def render_transaction_log():
    """
    Renders the transaction log page.
    """
    st.header("Transaction Log")

    # Get user profile for default ticker
    profile = up.get_user_profile()
    default_ticker = profile.get('default_ticker', 'AAPL') if profile else 'AAPL'

    # Form to add a new transaction
    with st.expander("Add New Transaction"):
        with st.form(key="add_transaction_form"):
            trans_ticker = st.text_input("Ticker", value=default_ticker)
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

    # Display all transactions
    st.subheader("Transaction History")
    
    # Allow filtering by ticker
    filter_ticker = st.text_input("Filter by ticker (leave empty for all):", "")
    
    if filter_ticker:
        transactions = trans.get_transactions(filter_ticker.upper())
        st.subheader(f"Transactions for {filter_ticker.upper()}")
    else:
        # Get all transactions - we need to modify this in transaction.py
        transactions = trans.get_transactions("")
        st.subheader("All Transactions")
    
    if not transactions:
        st.info(f"No transactions found.")
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
