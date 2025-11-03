# Example Configuration File
# 
# This file shows example configurations for different use cases.
# Copy the relevant settings to config/settings.py

# ============================================================================
# CONFIGURATION 1: Individual Trader (Default)
# ============================================================================
# Use free yfinance data source with moderate update frequency
# Good for: Individual traders, learning, development

DATABASE_FILE = "securities_data.db"
EXCHANGE_TIMEZONE = "America/New_York"
MARKET_OPEN_TIME = "09:30"
MARKET_CLOSE_TIME = "16:00"
MARKET_DAYS = [0, 1, 2, 3, 4]  # Monday to Friday

SUPPORTED_INTERVALS = {
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "1h": 60,
    "4h": 240,
    "1d": "daily"
}

PRIMARY_DATA_SOURCE = "yfinance"
ENABLE_REALTIME_UPDATES = True
UPDATE_CHECK_INTERVAL = 60  # Check every minute

# ============================================================================
# CONFIGURATION 2: Day Trader (High Frequency)
# ============================================================================
# Use premium data source with frequent updates
# Good for: Active day traders needing real-time data

DATABASE_FILE = "securities_data.db"
EXCHANGE_TIMEZONE = "America/New_York"
MARKET_OPEN_TIME = "09:30"
MARKET_CLOSE_TIME = "16:00"
MARKET_DAYS = [0, 1, 2, 3, 4]

SUPPORTED_INTERVALS = {
    "1m": 1,      # 1-minute intervals
    "5m": 5,
    "15m": 15,
    "1h": 60,
    "1d": "daily"
}

PRIMARY_DATA_SOURCE = "polygon"  # or "finnhub" for real-time data
POLYGON_API_KEY = "YOUR_API_KEY_HERE"  # Or set via environment variable
ENABLE_REALTIME_UPDATES = True
UPDATE_CHECK_INTERVAL = 30  # Check every 30 seconds for faster response

# ============================================================================
# CONFIGURATION 3: Swing Trader (Low Frequency)
# ============================================================================
# Use free data source with less frequent updates
# Good for: Swing traders, long-term investors

DATABASE_FILE = "securities_data.db"
EXCHANGE_TIMEZONE = "America/New_York"
MARKET_OPEN_TIME = "09:30"
MARKET_CLOSE_TIME = "16:00"
MARKET_DAYS = [0, 1, 2, 3, 4]

SUPPORTED_INTERVALS = {
    "1h": 60,
    "4h": 240,
    "1d": "daily",
    "1w": "weekly"
}

PRIMARY_DATA_SOURCE = "yfinance"
ENABLE_REALTIME_UPDATES = True
UPDATE_CHECK_INTERVAL = 300  # Check every 5 minutes (sufficient for hourly data)

# ============================================================================
# CONFIGURATION 4: Development/Testing
# ============================================================================
# Disable real-time updates for testing
# Good for: Development, backtesting, testing strategies

DATABASE_FILE = "test_securities_data.db"  # Separate test database
EXCHANGE_TIMEZONE = "America/New_York"
MARKET_OPEN_TIME = "09:30"
MARKET_CLOSE_TIME = "16:00"
MARKET_DAYS = [0, 1, 2, 3, 4]

SUPPORTED_INTERVALS = {
    "15m": 15,
    "1h": 60,
    "1d": "daily"
}

PRIMARY_DATA_SOURCE = "yfinance"
ENABLE_REALTIME_UPDATES = False  # Disable for manual control during testing
UPDATE_CHECK_INTERVAL = 60

# ============================================================================
# CONFIGURATION 5: Multi-Source with Fallback
# ============================================================================
# Use premium source with automatic fallback to free source
# Good for: Reliability, handling API outages

DATABASE_FILE = "securities_data.db"
EXCHANGE_TIMEZONE = "America/New_York"
MARKET_OPEN_TIME = "09:30"
MARKET_CLOSE_TIME = "16:00"
MARKET_DAYS = [0, 1, 2, 3, 4]

SUPPORTED_INTERVALS = {
    "5m": 5,
    "15m": 15,
    "1h": 60,
    "1d": "daily"
}

PRIMARY_DATA_SOURCE = "finnhub"  # Try finnhub first
FINNHUB_API_KEY = "YOUR_API_KEY_HERE"
# The system will automatically fallback to yfinance if finnhub fails
ENABLE_REALTIME_UPDATES = True
UPDATE_CHECK_INTERVAL = 60

# ============================================================================
# API KEY CONFIGURATION
# ============================================================================
# Best practice: Use environment variables for API keys
# Set these in your shell:
#
#   export FINNHUB_API_KEY="your_key"
#   export POLYGON_API_KEY="your_key"
#   export ALPHAVANTAGE_API_KEY="your_key"
#
# Alternatively, set them here (not recommended for production):

FINNHUB_API_KEY = ""  # Get from https://finnhub.io/
POLYGON_API_KEY = ""  # Get from https://polygon.io/
ALPHAVANTAGE_API_KEY = ""  # Get from https://www.alphavantage.co/

# ============================================================================
# ADVANCED: Custom Trading Hours
# ============================================================================
# For other exchanges or extended hours trading

# Example: Extended hours (pre-market and after-hours)
# MARKET_OPEN_TIME = "04:00"  # Pre-market starts 4 AM ET
# MARKET_CLOSE_TIME = "20:00"  # After-hours ends 8 PM ET

# Example: Different timezone (e.g., London Stock Exchange)
# EXCHANGE_TIMEZONE = "Europe/London"
# MARKET_OPEN_TIME = "08:00"
# MARKET_CLOSE_TIME = "16:30"
# MARKET_DAYS = [0, 1, 2, 3, 4]

# ============================================================================
# NOTES
# ============================================================================
# 
# Data Source Comparison:
# 
# yfinance:
#   - Free, no API key
#   - Good coverage of US stocks
#   - Delayed data (15-20 min typically)
#   - Best for: Learning, individual traders, long-term investing
#
# Finnhub:
#   - Free tier available (60 calls/min)
#   - Real-time data on paid plans
#   - Good coverage globally
#   - Best for: Active traders, international markets
#
# Polygon.io:
#   - Excellent data quality
#   - Real-time on paid plans
#   - Great for US markets
#   - Best for: Serious traders, institutions
#
# Alpha Vantage:
#   - Free tier: 5 calls/min
#   - Good for occasional updates
#   - More limited than others on free tier
#   - Best for: Small portfolios, low-frequency trading
#
# Update Frequency Guidelines:
#   - 30 seconds: For 1-minute interval data (day trading)
#   - 60 seconds: For 5-15 minute intervals (active trading)
#   - 300 seconds: For hourly intervals (swing trading)
#   - Manual: For daily data (can run once per day after market close)
