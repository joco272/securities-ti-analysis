import sys
import os
from datetime import date

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.portfolio.transaction import add_transaction
from src.portfolio.summary import get_portfolio_summary

if __name__ == '__main__':
    # --- Test block for portfolio calculation ---
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
