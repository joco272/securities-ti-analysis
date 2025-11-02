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

if __name__ == '__main__':
    # --- Test block for watchlist functionality ---
    print("Testing Watchlist Functionality...")
    # 1. Add new watchlists
    add_watchlist("My Tech Stocks")
    add_watchlist("Blue Chips")
    add_watchlist("My Tech Stocks") # Test duplicate

    # 2. Get all watchlists
    all_watchlists = get_watchlists()
    print("\nCurrent Watchlists:")
    for wl in all_watchlists:
        print(f"- ID: {wl['id']}, Name: {wl['name']}")

    # 3. Add tickers to a watchlist
    tech_watchlist_id = all_watchlists[1]['id'] # Assuming 'My Tech Stocks' is second alphabetically
    add_to_watchlist(tech_watchlist_id, "AAPL")
    add_to_watchlist(tech_watchlist_id, "GOOGL")
    add_to_watchlist(tech_watchlist_id, "MSFT")
    add_to_watchlist(tech_watchlist_id, "AAPL") # Test duplicate

    # 4. Get items from a watchlist
    tech_stocks = get_watchlist_items(tech_watchlist_id)
    print(f"\nItems in '{all_watchlists[1]['name']}':")
    for stock in tech_stocks:
        print(f"- ID: {stock['id']}, Ticker: {stock['ticker']}")

    # 5. Remove an item
    item_to_remove_id = tech_stocks[0]['id'] # Removing AAPL
    remove_from_watchlist(item_to_remove_id)
    print(f"\nRemoving item ID {item_to_remove_id}...")

    # 6. Verify removal
    updated_tech_stocks = get_watchlist_items(tech_watchlist_id)
    print(f"\nUpdated items in '{all_watchlists[1]['name']}':")
    for stock in updated_tech_stocks:
        print(f"- ID: {stock['id']}, Ticker: {stock['ticker']}")

    print("\nTest complete.")
