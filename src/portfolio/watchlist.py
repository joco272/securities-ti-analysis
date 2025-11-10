import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

def add_watchlist(name: str):
    """Adds a new watchlist to the database."""
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO watchlists (name) VALUES (?)", (name,))
        conn.commit()
    except conn.IntegrityError:
        # This error occurs if the watchlist name already exists
        print(f"Watchlist '{name}' already exists.")
    finally:
        conn.close()

def get_watchlists():
    """Returns a list of all watchlists."""
    conn = get_db_connection()
    watchlists = conn.execute("SELECT id, name FROM watchlists ORDER BY name").fetchall()
    conn.close()
    return watchlists

def add_to_watchlist(watchlist_id: int, ticker: str):
    """Adds a ticker to a specific watchlist."""
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO watchlist_items (watchlist_id, ticker) VALUES (?, ?)", (watchlist_id, ticker.upper()))
        conn.commit()
    except conn.IntegrityError:
        # This error occurs if the ticker is already in the watchlist
        print(f"Ticker '{ticker}' is already in the selected watchlist.")
    finally:
        conn.close()

def get_watchlist_items(watchlist_id: int):
    """Returns a list of all items in a specific watchlist."""
    conn = get_db_connection()
    items = conn.execute(
        "SELECT id, ticker FROM watchlist_items WHERE watchlist_id = ? ORDER BY ticker",
        (watchlist_id,)
    ).fetchall()
    conn.close()
    return items

def remove_from_watchlist(item_id: int):
    """Removes a specific item from a watchlist."""
    conn = get_db_connection()
    conn.execute("DELETE FROM watchlist_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

