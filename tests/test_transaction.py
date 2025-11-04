import sys
import os
from datetime import date

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.portfolio.transaction import add_transaction, get_transactions

if __name__ == '__main__':
    # --- Test block for transaction functionality ---
    print("Testing Transaction Functionality...")
    test_ticker = "TSLA"

    # 1. Add some transactions
    print(f"\nAdding transactions for {test_ticker}...")
    add_transaction(test_ticker, date(2023, 5, 15), "buy", 10, 170.50)
    add_transaction(test_ticker, date(2023, 8, 22), "buy", 5, 230.25)
    add_transaction(test_ticker, date(2023, 11, 5), "sell", 8, 215.80)

    # 2. Get all transactions for the ticker
    all_transactions = get_transactions(test_ticker)
    print(f"\nTransactions for {test_ticker}:")
    for t in all_transactions:
        print(f"- Date: {t['transaction_date']}, Type: {t['transaction_type']}, Qty: {t['quantity']}, Price: ${t['price_per_share']:.2f}")

    # Test another ticker with no transactions
    no_trans_ticker = "XOM"
    print(f"\nGetting transactions for {no_trans_ticker} (should be empty)...")
    no_transactions = get_transactions(no_trans_ticker)
    print(f"Found {len(no_transactions)} transactions for {no_trans_ticker}.")

    print("\nTest complete.")
