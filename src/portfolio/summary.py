import sys
import os
import pandas as pd
from collections import defaultdict
import yfinance as yf

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

def get_portfolio_summary():
    """
    Calculates current holdings and average cost basis from the transactions table.

    Returns:
        A list of dictionaries, where each dictionary represents a holding.
    """
    conn = get_db_connection()
    # Fetch all transactions and load them into a pandas DataFrame for easier calculation
    transactions_df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()

    if transactions_df.empty:
        return []

    # Dictionaries to hold aggregated data per ticker
    holdings = defaultdict(lambda: {'shares_bought': 0, 'cost_of_buys': 0, 'shares_sold': 0})

    for index, row in transactions_df.iterrows():
        ticker = row['ticker']
        if row['transaction_type'] == 'buy':
            holdings[ticker]['shares_bought'] += row['quantity']
            holdings[ticker]['cost_of_buys'] += row['quantity'] * row['price_per_share']
        elif row['transaction_type'] == 'sell':
            holdings[ticker]['shares_sold'] += row['quantity']

    # Calculate final portfolio summary
    portfolio = []
    for ticker, data in holdings.items():
        current_shares = data['shares_bought'] - data['shares_sold']

        # Only include stocks currently held in the portfolio
        if current_shares > 0:
            avg_cost_basis = data['cost_of_buys'] / data['shares_bought'] if data['shares_bought'] > 0 else 0
            portfolio.append({
                'ticker': ticker,
                'shares': current_shares,
                'average_cost': avg_cost_basis
            })

    # Sort by ticker for a consistent order
    portfolio = sorted(portfolio, key=lambda x: x['ticker'])

    # --- Step 2: Fetch current market prices and calculate market value/P&L ---
    if not portfolio:
        return []

    tickers = [h['ticker'] for h in portfolio]
    # Fetch the latest price data for all tickers at once
    ticker_data = yf.Tickers(tickers)

    for holding in portfolio:
        try:
            # yfinance provides data in a slightly nested structure
            # We access the most recent closing price
            last_price = ticker_data.tickers[holding['ticker']].history(period='1d')['Close'].iloc[-1]
            holding['current_price'] = last_price
            holding['market_value'] = holding['shares'] * last_price
            holding['unrealized_pl'] = (last_price - holding['average_cost']) * holding['shares']
        except IndexError:
            # This can happen if yfinance fails to fetch data for a ticker
            holding['current_price'] = None
            holding['market_value'] = None
            holding['unrealized_pl'] = None

    return portfolio


if __name__ == '__main__':
    # --- Test block for portfolio calculation ---
    # We will use the transaction module to add test data first
    from transaction import add_transaction
    from datetime import date

    print("Testing Portfolio Calculation Logic...")

    # Add some test data if it's not already there from previous tests
    add_transaction("TSLA", date(2023, 5, 15), "buy", 10, 170.50)
    add_transaction("NVDA", date(2023, 1, 10), "buy", 20, 150.00)

    summary = get_portfolio_summary()

    print("\n--- Portfolio Summary with Live Market Data ---")
    if not summary:
        print("Portfolio is empty or could not fetch data.")
    else:
        for holding in summary:
            print(
                f"Ticker: {holding['ticker']}, "
                f"Shares: {holding['shares']:.2f}, "
                f"Avg. Cost: ${holding['average_cost']:.2f}, "
                f"Current Price: ${holding.get('current_price', 0):.2f}, "
                f"Market Value: ${holding.get('market_value', 0):.2f}, "
                f"Unrealized P/L: ${holding.get('unrealized_pl', 0):.2f}"
            )

    print("\nTest complete.")
