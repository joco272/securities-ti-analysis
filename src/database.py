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
    Initializes the database by creating the necessary tables if they do not exist.
    This new schema is designed to be extensible for new indicators.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create the 'price_data' table for OHLCV data
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

    # Create the 'indicator_data' table for storing indicator values as JSON
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS indicator_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        price_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        values_json TEXT NOT NULL,
        FOREIGN KEY (price_id) REFERENCES price_data (id),
        UNIQUE(price_id, name)
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully with new extensible schema.")

if __name__ == '__main__':
    # Re-initialize the database with the new schema
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)
        print(f"Removed old database file: {DATABASE_FILE}")
    initialize_database()
