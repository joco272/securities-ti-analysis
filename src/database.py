import sqlite3

def initialize_database():
    """
    Initializes the SQLite database by creating all necessary tables if they don't already exist.
    """
    conn = sqlite3.connect('securities_data.db')
    cursor = conn.cursor()

    # Create price_data table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_data (
        id INTEGER PRIMARY KEY,
        ticker TEXT NOT NULL,
        interval TEXT NOT NULL,
        timestamp DATETIME NOT NULL,
        open REAL NOT NULL,
        high REAL NOT NULL,
        low REAL NOT NULL,
        close REAL NOT NULL,
        volume INTEGER NOT NULL,
        UNIQUE(ticker, interval, timestamp)
    )
    """)

    # Create indicator_data table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS indicator_data (
        price_id INTEGER,
        indicator_name TEXT NOT NULL,
        value TEXT NOT NULL, -- Storing complex indicators (like MACD) as JSON strings
        FOREIGN KEY (price_id) REFERENCES price_data (id),
        PRIMARY KEY (price_id, indicator_name)
    )
    """)

    # Create watchlists table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS watchlists (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    )
    """)

    # Create watchlist_items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS watchlist_items (
        id INTEGER PRIMARY KEY,
        watchlist_id INTEGER,
        ticker TEXT NOT NULL,
        FOREIGN KEY (watchlist_id) REFERENCES watchlists (id),
        UNIQUE(watchlist_id, ticker)
    )
    """)

    # Create transactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        ticker TEXT NOT NULL,
        transaction_type TEXT NOT NULL, -- 'BUY' or 'SELL'
        quantity REAL NOT NULL,
        price REAL NOT NULL,
        transaction_date DATETIME NOT NULL
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    initialize_database()
