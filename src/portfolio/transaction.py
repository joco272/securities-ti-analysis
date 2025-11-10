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

