import sys
import os
from datetime import date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

def add_transaction(ticker: str, trans_date: date, trans_type: str, quantity: float, price: float):
    """Adds a new transaction to the database."""
    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO transactions (ticker, transaction_date, transaction_type, quantity, price_per_share)
        VALUES (?, ?, ?, ?, ?)
        """,
        (ticker.upper(), trans_date.isoformat(), trans_type, quantity, price)
    )
    conn.commit()
    conn.close()

def get_transactions(ticker: str):
    """Returns a list of all transactions for a specific ticker."""
    conn = get_db_connection()
    transactions = conn.execute(
        "SELECT id, transaction_date, transaction_type, quantity, price_per_share FROM transactions WHERE ticker = ? ORDER BY transaction_date DESC",
        (ticker.upper(),)
    ).fetchall()
    conn.close()
    return transactions

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
