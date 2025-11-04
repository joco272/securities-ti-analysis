import sys
import os

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.portfolio.watchlist import add_watchlist, get_watchlists, add_to_watchlist, get_watchlist_items, remove_from_watchlist

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
