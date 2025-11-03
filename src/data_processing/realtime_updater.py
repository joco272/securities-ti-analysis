"""
Real-time Technical Indicator Updater

This module handles automatic updates of technical indicators at interval close times
based on exchange operating hours.
"""
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pytz
import schedule
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    EXCHANGE_TIMEZONE,
    MARKET_OPEN_TIME,
    MARKET_CLOSE_TIME,
    MARKET_DAYS,
    SUPPORTED_INTERVALS,
    ENABLE_REALTIME_UPDATES,
    UPDATE_CHECK_INTERVAL
)
from data_processing.data_retrieval import fetch_ohlcv
from data_processing.indicators import calculate_indicators
from data_processing.data_storage import write_indicators_to_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def is_market_open() -> bool:
    """
    Check if the market is currently open based on NYSE hours.
    
    Returns:
        bool: True if market is open, False otherwise
    """
    tz = pytz.timezone(EXCHANGE_TIMEZONE)
    now = datetime.now(tz)
    
    # Check if today is a trading day (Monday-Friday)
    if now.weekday() not in MARKET_DAYS:
        return False
    
    # Parse market open and close times
    market_open = datetime.strptime(MARKET_OPEN_TIME, "%H:%M").time()
    market_close = datetime.strptime(MARKET_CLOSE_TIME, "%H:%M").time()
    current_time = now.time()
    
    return market_open <= current_time <= market_close


def get_next_interval_close(interval_minutes: int) -> Optional[datetime]:
    """
    Calculate the next interval close time.
    
    For example, if it's 8:33 AM and interval is 5 minutes,
    the next close is 8:35 AM.
    
    Args:
        interval_minutes: The interval in minutes (e.g., 5, 15, 30, 60)
    
    Returns:
        datetime: The next interval close time in exchange timezone
    """
    tz = pytz.timezone(EXCHANGE_TIMEZONE)
    now = datetime.now(tz)
    
    # Parse market open time
    market_open = datetime.strptime(MARKET_OPEN_TIME, "%H:%M").time()
    market_open_dt = datetime.combine(now.date(), market_open).replace(tzinfo=tz)
    
    # Calculate minutes since market open
    minutes_since_open = (now - market_open_dt).total_seconds() / 60
    
    if minutes_since_open < 0:
        # Market hasn't opened yet today
        return market_open_dt + timedelta(minutes=interval_minutes)
    
    # Calculate the next interval close
    intervals_passed = int(minutes_since_open / interval_minutes)
    next_close = market_open_dt + timedelta(minutes=(intervals_passed + 1) * interval_minutes)
    
    return next_close


def should_update_now(interval: str) -> bool:
    """
    Check if we should update indicators now based on the interval.
    
    Args:
        interval: The interval string (e.g., '5m', '15m', '1h', '1d')
    
    Returns:
        bool: True if an update should occur now
    """
    if not is_market_open():
        return False
    
    interval_value = SUPPORTED_INTERVALS.get(interval)
    if not interval_value:
        logger.warning(f"Unsupported interval: {interval}")
        return False
    
    # Daily interval updates at market close
    if interval_value == "daily":
        tz = pytz.timezone(EXCHANGE_TIMEZONE)
        now = datetime.now(tz)
        market_close = datetime.strptime(MARKET_CLOSE_TIME, "%H:%M").time()
        current_time = now.time()
        
        # Update within 1 minute of market close
        close_dt = datetime.combine(now.date(), market_close).replace(tzinfo=tz)
        time_diff = abs((now - close_dt).total_seconds())
        return time_diff < 60
    
    # Intraday intervals
    next_close = get_next_interval_close(interval_value)
    if not next_close:
        return False
    
    tz = pytz.timezone(EXCHANGE_TIMEZONE)
    now = datetime.now(tz)
    
    # Check if we're within 1 minute of the interval close
    time_diff = (next_close - now).total_seconds()
    return -60 < time_diff < 60


def update_ticker_indicators(ticker: str, interval: str):
    """
    Update indicators for a specific ticker and interval.
    
    Args:
        ticker: The stock ticker symbol
        interval: The data interval (e.g., '5m', '15m', '1h', '1d')
    """
    try:
        logger.info(f"Updating indicators for {ticker} at {interval} interval")
        
        # Fetch recent data (last 100 periods to ensure we have enough for indicators)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Calculate appropriate start date based on interval
        interval_value = SUPPORTED_INTERVALS.get(interval)
        if interval_value == "daily":
            start_date = (datetime.now() - timedelta(days=200)).strftime("%Y-%m-%d")
        else:
            # For intraday, fetch last 7 days
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        ohlcv_data = fetch_ohlcv(ticker, start_date, end_date, interval)
        
        if ohlcv_data.empty:
            logger.warning(f"No data fetched for {ticker} at {interval}")
            return
        
        # Calculate indicators
        data_with_indicators = calculate_indicators(ohlcv_data)
        
        # Store in database
        write_indicators_to_db(ticker, interval, data_with_indicators)
        
        logger.info(f"Successfully updated {ticker} at {interval} - {len(data_with_indicators)} records")
        
    except Exception as e:
        logger.error(f"Error updating {ticker} at {interval}: {e}")


def update_watchlist_indicators(watchlist_tickers: List[str], intervals: List[str]):
    """
    Update indicators for all tickers in a watchlist.
    
    Args:
        watchlist_tickers: List of ticker symbols to update
        intervals: List of intervals to update (e.g., ['5m', '15m', '1h', '1d'])
    """
    for ticker in watchlist_tickers:
        for interval in intervals:
            if should_update_now(interval):
                update_ticker_indicators(ticker, interval)


class RealtimeUpdater:
    """
    Background service that manages real-time indicator updates.
    """
    
    def __init__(self, watchlist_tickers: List[str], intervals: List[str]):
        """
        Initialize the realtime updater.
        
        Args:
            watchlist_tickers: List of ticker symbols to monitor
            intervals: List of intervals to update
        """
        self.watchlist_tickers = watchlist_tickers
        self.intervals = intervals
        self.running = False
        
    def check_and_update(self):
        """Check if updates are needed and perform them."""
        if not ENABLE_REALTIME_UPDATES:
            return
        
        logger.info("Checking for updates...")
        update_watchlist_indicators(self.watchlist_tickers, self.intervals)
    
    def start(self):
        """Start the realtime updater service."""
        if not ENABLE_REALTIME_UPDATES:
            logger.info("Realtime updates are disabled in settings")
            return
        
        self.running = True
        logger.info(f"Starting realtime updater for tickers: {self.watchlist_tickers}")
        logger.info(f"Monitoring intervals: {self.intervals}")
        
        # Schedule the update check
        schedule.every(UPDATE_CHECK_INTERVAL).seconds.do(self.check_and_update)
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Realtime updater stopped by user")
            self.running = False
    
    def stop(self):
        """Stop the realtime updater service."""
        self.running = False
        schedule.clear()
        logger.info("Realtime updater stopped")


def run_updater_service(watchlist_tickers: List[str], intervals: List[str]):
    """
    Convenience function to run the updater service.
    
    Args:
        watchlist_tickers: List of ticker symbols to monitor
        intervals: List of intervals to update
    """
    updater = RealtimeUpdater(watchlist_tickers, intervals)
    updater.start()


if __name__ == '__main__':
    # Example usage
    example_tickers = ['AAPL', 'MSFT', 'GOOGL']
    example_intervals = ['5m', '15m', '1h', '1d']
    
    logger.info("Starting realtime updater service...")
    logger.info(f"Market timezone: {EXCHANGE_TIMEZONE}")
    logger.info(f"Market hours: {MARKET_OPEN_TIME} - {MARKET_CLOSE_TIME}")
    
    run_updater_service(example_tickers, example_intervals)
