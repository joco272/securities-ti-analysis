import sqlite3
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import DATABASE_FILE

def get_db_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """
    Initializes the database by creating all necessary tables for price data,
    indicators, and portfolio management if they do not already exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Price and Indicator Tables ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        ticker TEXT NOT NULL,
        interval TEXT NOT NULL,
        open REAL NOT NULL,
        high REAL NOT NULL,
        low REAL NOT NULL,
        close REAL NOT NULL,
        volume INTEGER NOT NULL,
        UNIQUE(timestamp, ticker, interval)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS indicator_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        price_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        values_json TEXT NOT NULL,
        FOREIGN KEY (price_id) REFERENCES price_data (id) ON DELETE CASCADE,
        UNIQUE(price_id, name)
    )
    """)

    # --- Portfolio Management Tables ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS watchlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS watchlist_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        watchlist_id INTEGER NOT NULL,
        ticker TEXT NOT NULL,
        FOREIGN KEY (watchlist_id) REFERENCES watchlists (id) ON DELETE CASCADE,
        UNIQUE(watchlist_id, ticker)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        transaction_date TEXT NOT NULL,
        transaction_type TEXT NOT NULL CHECK(transaction_type IN ('buy', 'sell')),
        quantity REAL NOT NULL,
        price_per_share REAL NOT NULL
    )
    """)

    # --- User Profile Table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT,
        default_ticker TEXT NOT NULL,
        default_interval TEXT NOT NULL,
        risk_tolerance TEXT NOT NULL CHECK(risk_tolerance IN ('Low', 'Medium', 'High'))
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    # This will ensure all tables are created if the file is run directly.
    # It's safe to run multiple times.
    initialize_database()
