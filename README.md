# Securities Technical Indicator Analysis

A comprehensive securities analysis and news aggregator application with real-time technical indicator updates, machine learning-based trading strategies, and portfolio management.

## Features

### Core Features

1. **Technical Indicator Calculation and Storage**
   - Calculates and stores technical indicators: MACD, MFI, RSI, Stochastic RSI, A/D, OBV, SMA, Awesome Oscillator
   - Supports multiple time intervals: 5m, 15m, 30m, 1h, 4h, 1d
   - Data stored in local SQLite database

2. **Real-time Indicator Updates**
   - Automatic updates at interval close times (e.g., 8:35 AM, 8:40 AM for 5-minute intervals)
   - Updates synchronized with NYSE operating hours (9:30 AM - 4:00 PM ET)
   - Configurable update intervals and monitoring schedules

3. **Machine Learning Models for Buy/Sell Signals**
   - Backtesting framework with RSI-based strategy
   - Performance metrics: Sharpe ratio, win/loss ratio
   - Extensible for custom trading strategies

4. **Multiple Data Source Support**
   - Primary: yfinance (free, no API key required)
   - Optional: Finnhub, Polygon.io, Alpha Vantage (requires API keys)
   - Automatic fallback to yfinance if primary source fails

5. **Portfolio Management**
   - Track holdings and transactions
   - Monitor multiple watchlists
   - View portfolio summary with P&L

6. **Interactive Visualization**
   - Multi-pane charts with technical indicators
   - Streamlit-based user interface

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Initialize Database

```bash
python src/database.py
```

## Usage

### Running the Web Application

The main application provides an interactive interface for analysis and portfolio management:

```bash
streamlit run src/app.py
```

Access the application at `http://localhost:8501`

### Running the Real-time Updater Service

The real-time updater runs as a background service to automatically update indicators:

```bash
python scripts/run_updater_service.py
```

This service will:
- Monitor all tickers in your watchlists
- Update indicators at interval close times during market hours
- Log all updates for monitoring

**Note:** The updater checks every minute if an update is needed based on the configured intervals.

### Configuration

Edit `config/settings.py` to customize:

```python
# Exchange Operating Hours (NYSE - Eastern Time)
EXCHANGE_TIMEZONE = "America/New_York"
MARKET_OPEN_TIME = "09:30"  # 9:30 AM ET
MARKET_CLOSE_TIME = "16:00"  # 4:00 PM ET

# Data Source (options: 'yfinance', 'finnhub', 'polygon', 'alphavantage')
PRIMARY_DATA_SOURCE = "yfinance"

# Enable/Disable Real-time Updates
ENABLE_REALTIME_UPDATES = True
UPDATE_CHECK_INTERVAL = 60  # Check every 60 seconds
```

### Setting Up API Keys (Optional)

For data sources other than yfinance, set environment variables:

```bash
# For Finnhub
export FINNHUB_API_KEY="your_api_key_here"

# For Polygon.io
export POLYGON_API_KEY="your_api_key_here"

# For Alpha Vantage
export ALPHAVANTAGE_API_KEY="your_api_key_here"
```

Or edit `config/settings.py` directly (not recommended for production).

## Project Structure

```
securities-ti-analysis/
├── config/
│   ├── __init__.py
│   └── settings.py              # Configuration settings
├── src/
│   ├── data_processing/
│   │   ├── data_retrieval.py    # Fetch market data
│   │   ├── data_sources.py      # Multi-source data abstraction
│   │   ├── data_storage.py      # Store data in database
│   │   ├── data_query.py        # Query data from database
│   │   ├── indicators.py        # Calculate technical indicators
│   │   └── realtime_updater.py  # Real-time update service
│   ├── ml_models/
│   │   └── backtesting_framework.py  # Backtesting strategies
│   ├── portfolio/
│   │   ├── watchlist.py         # Watchlist management
│   │   ├── transaction.py       # Transaction tracking
│   │   └── summary.py           # Portfolio summary
│   ├── plotting/
│   │   └── charts.py            # Visualization
│   ├── database.py              # Database initialization
│   └── app.py                   # Main Streamlit app
├── scripts/
│   └── run_updater_service.py   # Standalone updater service
├── tests/
├── requirements.txt
└── PRODUCT_REQUIREMENT_DOCUMENT.md
```

## How Real-time Updates Work

The real-time updater follows exchange operating hours and updates indicators at precise interval close times:

### Example: 5-minute Interval

If the market opens at 9:30 AM:
- First update: 9:35 AM (5 minutes after open)
- Second update: 9:40 AM
- Third update: 9:45 AM
- And so on until market close at 4:00 PM

### Update Logic

1. **Market Hours Check**: Only updates during NYSE trading hours (Mon-Fri, 9:30 AM - 4:00 PM ET)
2. **Interval Calculation**: Calculates next interval close time based on market open
3. **Scheduled Updates**: Checks every minute if an update is due (within 1 minute of close)
4. **Data Fetch**: Fetches latest data from configured source
5. **Indicator Calculation**: Calculates all technical indicators
6. **Storage**: Stores results in SQLite database

### Supported Intervals

- **Intraday**: 5m, 15m, 30m, 1h, 4h
- **Daily**: 1d (updates at market close)

## Data Sources

### yfinance (Default)
- **Pros**: Free, no API key required, reliable
- **Cons**: Limited to what Yahoo Finance provides
- **Best for**: Individual traders, development, testing

### Finnhub
- **Pros**: Good coverage, real-time data
- **Cons**: Requires API key, rate limits on free tier
- **Best for**: Professional traders needing real-time data

### Polygon.io
- **Pros**: Excellent data quality, comprehensive coverage
- **Cons**: Requires API key, paid plans for full access
- **Best for**: Serious traders and institutions

### Alpha Vantage
- **Pros**: Free tier available, good documentation
- **Cons**: Strict rate limits (5 calls/minute free tier)
- **Best for**: Low-frequency updates, small portfolios

## Technical Indicators

The application calculates the following indicators:

- **MACD**: Moving Average Convergence Divergence
- **RSI**: Relative Strength Index (14-period)
- **MFI**: Money Flow Index
- **Stochastic RSI**: Stochastic Relative Strength Index
- **A/D**: Accumulation/Distribution Line
- **OBV**: On-Balance Volume
- **SMA**: Simple Moving Averages (50 and 200-period)
- **AO**: Awesome Oscillator

## Backtesting

The application includes a backtesting framework using the `backtesting.py` library:

```python
# Example RSI Strategy
class RsiOscillator(Strategy):
    upper_bound = 70
    lower_bound = 30
    
    def next(self):
        if crossover(self.data.rsi, self.upper_bound):
            self.position.close()
        elif crossover(self.lower_bound, self.data.rsi):
            self.buy()
```

Performance metrics include:
- Sharpe Ratio
- Win Rate
- Maximum Drawdown
- Total Return

## Development

### Running Tests

```bash
pytest tests/
```

### Adding New Indicators

1. Add calculation in `src/data_processing/indicators.py`
2. Update storage logic in `src/data_processing/data_storage.py`
3. Update query logic in `src/data_processing/data_query.py`

### Adding New Data Sources

1. Implement fetch function in `src/data_processing/data_sources.py`
2. Add to `source_map` in `fetch_ohlcv_multi_source()`
3. Update configuration in `config/settings.py`

## Deployment

### Running as a Service (Linux)

Create a systemd service file `/etc/systemd/system/securities-updater.service`:

```ini
[Unit]
Description=Securities Real-time Indicator Updater
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/securities-ti-analysis
ExecStart=/usr/bin/python3 scripts/run_updater_service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable securities-updater
sudo systemctl start securities-updater
sudo systemctl status securities-updater
```

### Running with Docker (Future)

Docker support is planned for easier deployment and scalability.

## Troubleshooting

### Issue: No data fetched

**Solution**: Check your internet connection and data source configuration. Try switching to yfinance.

### Issue: API rate limits

**Solution**: 
- Reduce update frequency in `config/settings.py`
- Upgrade to a paid API plan
- Switch to yfinance (no rate limits)

### Issue: Database locked

**Solution**: Only one process should write to the database at a time. Stop the updater service before running manual updates.

## License

See repository for license information.

## Contributing

Contributions are welcome! Please submit issues and pull requests.

## Roadmap

- [ ] Add more technical indicators
- [ ] Support for cryptocurrency markets
- [ ] Email/SMS alerts for trading signals
- [ ] Web-based dashboard (FastAPI backend)
- [ ] Docker containerization
- [ ] Cloud deployment guides
- [ ] More sophisticated ML models
- [ ] News sentiment analysis integration

## Support

For issues, questions, or contributions, please open an issue on GitHub.
