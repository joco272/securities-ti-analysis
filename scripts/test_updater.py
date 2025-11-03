#!/usr/bin/env python3
"""
Test script for the real-time updater functionality.

This script helps test and debug the real-time update logic without running
the full service.
"""
import sys
import os
from datetime import datetime, timedelta

# Add src directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, '..', 'src')
config_dir = os.path.join(script_dir, '..', 'config')
sys.path.insert(0, src_dir)
sys.path.insert(0, os.path.dirname(src_dir))

from data_processing.realtime_updater import (
    is_market_open,
    get_next_interval_close,
    should_update_now,
    update_ticker_indicators
)
from config.settings import EXCHANGE_TIMEZONE, MARKET_OPEN_TIME, MARKET_CLOSE_TIME
import pytz


def print_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_market_status():
    """Test and display current market status."""
    print_header("Market Status")
    
    tz = pytz.timezone(EXCHANGE_TIMEZONE)
    now = datetime.now(tz)
    
    print(f"Current time (ET): {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Day of week: {now.strftime('%A')}")
    print(f"Market hours: {MARKET_OPEN_TIME} - {MARKET_CLOSE_TIME} {EXCHANGE_TIMEZONE}")
    print(f"Market is open: {'✓ YES' if is_market_open() else '✗ NO'}")
    
    if not is_market_open():
        # Calculate next market open
        market_open = datetime.strptime(MARKET_OPEN_TIME, "%H:%M").time()
        
        # If after close today, next open is tomorrow
        if now.time() > datetime.strptime(MARKET_CLOSE_TIME, "%H:%M").time():
            days_ahead = 1
            if now.weekday() == 4:  # Friday
                days_ahead = 3  # Skip to Monday
        else:
            days_ahead = 0
            if now.weekday() == 5:  # Saturday
                days_ahead = 2
            elif now.weekday() == 6:  # Sunday
                days_ahead = 1
        
        next_open = now + timedelta(days=days_ahead)
        next_open = next_open.replace(
            hour=market_open.hour,
            minute=market_open.minute,
            second=0,
            microsecond=0
        )
        
        print(f"Next market open: {next_open.strftime('%Y-%m-%d %H:%M %Z')}")


def test_interval_closes():
    """Test and display next interval close times."""
    print_header("Interval Close Times")
    
    if not is_market_open():
        print("Market is closed. Interval close times are calculated for when market is open.")
        return
    
    intervals = [
        (5, "5-minute"),
        (15, "15-minute"),
        (30, "30-minute"),
        (60, "1-hour"),
        (240, "4-hour")
    ]
    
    for interval_min, name in intervals:
        next_close = get_next_interval_close(interval_min)
        if next_close:
            time_until = (next_close - datetime.now(pytz.timezone(EXCHANGE_TIMEZONE))).total_seconds()
            minutes_until = int(time_until / 60)
            seconds_until = int(time_until % 60)
            
            print(f"{name:15} → Next close: {next_close.strftime('%H:%M:%S')} "
                  f"(in {minutes_until}m {seconds_until}s)")


def test_update_triggers():
    """Test which intervals should trigger updates now."""
    print_header("Update Triggers")
    
    if not is_market_open():
        print("Market is closed. No updates will trigger.")
        return
    
    intervals = ['5m', '15m', '30m', '1h', '4h', '1d']
    
    print("Checking which intervals should update now...")
    print()
    
    any_update = False
    for interval in intervals:
        should_update = should_update_now(interval)
        status = "✓ UPDATE NOW" if should_update else "✗ No update"
        print(f"{interval:5} → {status}")
        if should_update:
            any_update = True
    
    if not any_update:
        print("\nNo intervals need updating at this moment.")
        print("Updates occur within 1 minute of interval close times.")


def test_manual_update(ticker, interval):
    """Perform a manual update for testing."""
    print_header(f"Manual Update: {ticker} @ {interval}")
    
    print(f"Attempting to update {ticker} with {interval} interval...")
    print("This will fetch data and calculate indicators.")
    print()
    
    try:
        update_ticker_indicators(ticker, interval)
        print(f"\n✓ Successfully updated {ticker}")
    except Exception as e:
        print(f"\n✗ Update failed: {e}")


def main():
    """Main test function."""
    print("\n" + "=" * 60)
    print("  REAL-TIME UPDATER TEST SCRIPT")
    print("=" * 60)
    
    # Test market status
    test_market_status()
    
    # Test interval closes
    test_interval_closes()
    
    # Test update triggers
    test_update_triggers()
    
    # Optional: Perform manual update
    print("\n" + "=" * 60)
    response = input("\nPerform a manual update test? (y/n): ").strip().lower()
    
    if response == 'y':
        ticker = input("Enter ticker symbol (e.g., AAPL): ").strip().upper()
        interval = input("Enter interval (e.g., 1d, 1h, 15m): ").strip().lower()
        
        if ticker and interval:
            test_manual_update(ticker, interval)
        else:
            print("Invalid input. Skipping manual update.")
    
    print("\n" + "=" * 60)
    print("  Test complete!")
    print("=" * 60)
    print()


if __name__ == '__main__':
    main()
