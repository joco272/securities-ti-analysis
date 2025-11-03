#!/usr/bin/env python3
"""
Script to run the real-time indicator updater service.

This script can be run as a background service to continuously update
technical indicators at interval close times.

Usage:
    python scripts/run_updater_service.py

The script will read tickers from watchlists in the database and update
indicators for all configured intervals.
"""
import sys
import os

# Add src and parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, '..', 'src')
sys.path.insert(0, src_dir)
sys.path.insert(0, os.path.dirname(src_dir))

from data_processing.realtime_updater import run_updater_service
from portfolio.watchlist import get_watchlists, get_watchlist_items
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_all_watchlist_tickers():
    """
    Retrieve all unique tickers from all watchlists in the database.
    
    Returns:
        List of ticker symbols
    """
    all_tickers = set()
    
    try:
        watchlists = get_watchlists()
        for watchlist in watchlists:
            items = get_watchlist_items(watchlist['id'])
            for item in items:
                all_tickers.add(item['ticker'])
    except Exception as e:
        logger.error(f"Error fetching watchlist tickers: {e}")
    
    return list(all_tickers)


def main():
    """Main entry point for the updater service."""
    logger.info("=" * 60)
    logger.info("Real-time Technical Indicator Updater Service")
    logger.info("=" * 60)
    
    # Get tickers from watchlists
    tickers = get_all_watchlist_tickers()
    
    if not tickers:
        logger.warning("No tickers found in watchlists. Using default tickers.")
        tickers = ['AAPL', 'MSFT', 'GOOGL']  # Default tickers if no watchlists exist
    
    logger.info(f"Monitoring {len(tickers)} tickers: {', '.join(tickers)}")
    
    # Configure intervals to update
    intervals = ['5m', '15m', '1h', '4h', '1d']
    logger.info(f"Updating intervals: {', '.join(intervals)}")
    
    # Start the updater service
    try:
        run_updater_service(tickers, intervals)
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as e:
        logger.error(f"Service error: {e}")
        raise


if __name__ == '__main__':
    main()
