# Database Settings

# SQLite Database
DATABASE_FILE = "securities_data.db"

# Exchange Operating Hours (NYSE - Eastern Time)
EXCHANGE_TIMEZONE = "America/New_York"
MARKET_OPEN_TIME = "09:30"  # 9:30 AM ET
MARKET_CLOSE_TIME = "16:00"  # 4:00 PM ET
MARKET_DAYS = [0, 1, 2, 3, 4]  # Monday=0 to Friday=4

# Supported Intervals (in minutes for intraday, or special codes)
SUPPORTED_INTERVALS = {
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "1h": 60,
    "4h": 240,
    "1d": "daily"
}

# Data Source Configuration
# Options: 'yfinance', 'finnhub', 'polygon', 'alphavantage'
PRIMARY_DATA_SOURCE = "yfinance"

# API Keys (set environment variables for production)
FINNHUB_API_KEY = ""  # Set via environment variable: FINNHUB_API_KEY
POLYGON_API_KEY = ""  # Set via environment variable: POLYGON_API_KEY
ALPHAVANTAGE_API_KEY = ""  # Set via environment variable: ALPHAVANTAGE_API_KEY

# Real-time Update Settings
ENABLE_REALTIME_UPDATES = True
UPDATE_CHECK_INTERVAL = 60  # Check every 60 seconds if an update is needed
