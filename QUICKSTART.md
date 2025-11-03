# Quick Start Guide

This guide will help you get started with the Securities Technical Indicator Analysis application.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/joco272/securities-ti-analysis.git
   cd securities-ti-analysis
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database:**
   ```bash
   python src/database.py
   ```

## Basic Usage

### 1. Manual Analysis (One-time)

To fetch data, calculate indicators, and backtest for a specific ticker:

```bash
# Start the Streamlit app
streamlit run src/app.py
```

Then in the web interface:
1. Enter a ticker symbol (e.g., AAPL)
2. Select an interval (e.g., 1d)
3. Choose date range
4. Click "Fetch, Store, and Analyze"

### 2. Real-time Updates (Automated)

To enable automatic updates during market hours:

**Step 1: Add tickers to your watchlist**
- Open the Streamlit app
- Use the sidebar to create a watchlist
- Add tickers to your watchlist

**Step 2: Start the updater service**
```bash
python scripts/run_updater_service.py
```

The service will:
- Monitor your watchlists
- Check every minute if an update is needed
- Update indicators at interval close times
- Only run during market hours (9:30 AM - 4:00 PM ET, Mon-Fri)

### 3. Portfolio Management

Track your trades and holdings:

1. Open the Streamlit app
2. Scroll to "Transaction Log"
3. Add your buy/sell transactions
4. View your portfolio summary at the top

## Configuration

### Basic Configuration

Edit `config/settings.py` to customize:

```python
# Choose your primary data source
PRIMARY_DATA_SOURCE = "yfinance"  # Options: yfinance, finnhub, polygon, alphavantage

# Enable/disable real-time updates
ENABLE_REALTIME_UPDATES = True

# How often to check for updates (in seconds)
UPDATE_CHECK_INTERVAL = 60
```

### Using Alternative Data Sources

If you want to use Finnhub, Polygon.io, or Alpha Vantage:

1. **Get an API key** from your chosen provider
2. **Set environment variable:**
   ```bash
   export FINNHUB_API_KEY="your_key_here"
   # or
   export POLYGON_API_KEY="your_key_here"
   # or
   export ALPHAVANTAGE_API_KEY="your_key_here"
   ```
3. **Update settings:**
   ```python
   # In config/settings.py
   PRIMARY_DATA_SOURCE = "finnhub"  # or polygon, alphavantage
   ```

## Real-time Updates Explained

### How It Works

The updater service calculates the next interval close time based on market open:

**Example: 5-minute interval**
- Market opens: 9:30 AM
- First close: 9:35 AM ← Update happens here
- Second close: 9:40 AM ← Update happens here
- Third close: 9:45 AM ← Update happens here
- ... continues until market close at 4:00 PM

### Update Schedule

| Interval | Update Frequency | Updates per Day |
|----------|-----------------|-----------------|
| 5m       | Every 5 minutes | ~78 updates     |
| 15m      | Every 15 minutes| ~26 updates     |
| 30m      | Every 30 minutes| ~13 updates     |
| 1h       | Every hour      | ~6 updates      |
| 4h       | Every 4 hours   | ~2 updates      |
| 1d       | At market close | 1 update        |

### Market Hours

- **Exchange:** NYSE
- **Timezone:** America/New_York (Eastern Time)
- **Open:** 9:30 AM ET
- **Close:** 4:00 PM ET
- **Trading Days:** Monday - Friday

The service automatically:
- Checks if it's a trading day
- Verifies market is open
- Calculates correct interval close times
- Skips updates outside market hours

## Common Workflows

### Workflow 1: Analyze a New Stock

1. Open Streamlit app
2. Enter ticker (e.g., TSLA)
3. Select interval and date range
4. Click "Fetch, Store, and Analyze"
5. View charts and indicators
6. Review backtest results

### Workflow 2: Monitor Portfolio in Real-time

1. Create watchlist with your holdings
2. Add tickers to watchlist
3. Start updater service in background:
   ```bash
   nohup python scripts/run_updater_service.py > updater.log 2>&1 &
   ```
4. Open Streamlit app to view latest data
5. Service continuously updates during market hours

### Workflow 3: Compare Multiple Stocks

1. Add all stocks to a watchlist
2. Let updater service collect data
3. Use Streamlit app to analyze each ticker
4. Compare indicators across stocks

## Tips and Best Practices

### Performance

- **Start small:** Begin with 3-5 tickers, then expand
- **Choose intervals wisely:** More frequent intervals = more data and processing
- **Monitor disk space:** Database grows with more tickers and intervals

### Data Management

- **Regular backups:** Backup `securities_data.db` regularly
- **Clean old data:** Periodically clean up old data if needed
- **API limits:** Be aware of rate limits if using paid data sources

### Trading

- **Paper trading first:** Test strategies before real trading
- **Understand indicators:** Learn what each indicator means
- **Backtest thoroughly:** Always backtest strategies on historical data
- **Risk management:** Never risk more than you can afford to lose

## Troubleshooting

### Service won't start

**Problem:** Updater service fails to start

**Solutions:**
- Check Python path: `which python3`
- Verify dependencies: `pip list | grep schedule`
- Check logs for errors
- Ensure database is initialized

### No data being fetched

**Problem:** Updater runs but no data appears

**Solutions:**
- Verify market is open (Mon-Fri, 9:30 AM - 4:00 PM ET)
- Check internet connection
- Try switching data source to yfinance
- Review logs: `tail -f updater.log`

### Database is locked

**Problem:** "Database is locked" error

**Solutions:**
- Only run one updater service at a time
- Close Streamlit app before manual updates
- Check for orphaned processes: `ps aux | grep python`

## Next Steps

- **Customize indicators:** Add your own technical indicators
- **Build strategies:** Create custom backtesting strategies
- **Automate trading:** Integrate with broker API (future)
- **Set alerts:** Add price/indicator alerts (future)

## Getting Help

- Review the main [README.md](README.md) for detailed documentation
- Check [PRODUCT_REQUIREMENT_DOCUMENT.md](PRODUCT_REQUIREMENT_DOCUMENT.md) for architecture details
- Open an issue on GitHub for bugs or questions

## Example Commands

```bash
# Initialize everything
python src/database.py
python -c "from src.database import initialize_database; initialize_database()"

# Run interactive analysis
streamlit run src/app.py

# Start background updater (foreground)
python scripts/run_updater_service.py

# Start background updater (background)
nohup python scripts/run_updater_service.py > logs/updater.log 2>&1 &

# Check if updater is running
ps aux | grep run_updater_service.py

# Stop background updater
pkill -f run_updater_service.py

# View updater logs
tail -f logs/updater.log

# Test data fetch manually
python src/data_processing/data_retrieval.py

# Test indicator calculation
python src/data_processing/indicators.py
```

## Advanced Usage

### Running as System Service (Linux)

See [README.md](README.md) for systemd service configuration.

### Docker Deployment (Coming Soon)

Docker support is planned for easier deployment.

### Custom Strategies

To add a custom backtesting strategy:

1. Edit `src/ml_models/backtesting_framework.py`
2. Create a new Strategy class
3. Implement `init()` and `next()` methods
4. Update `run_backtest()` to use your strategy

Example:
```python
class MyCustomStrategy(Strategy):
    def init(self):
        self.sma = self.I(lambda x: talib.SMA(x, 20), self.data.Close)
    
    def next(self):
        if self.data.Close[-1] > self.sma[-1]:
            if not self.position:
                self.buy()
        elif self.data.Close[-1] < self.sma[-1]:
            if self.position:
                self.position.close()
```

## Support

For questions, issues, or contributions:
- GitHub Issues: [Report bugs or request features]
- Documentation: [README.md](README.md)
- Product Requirements: [PRODUCT_REQUIREMENT_DOCUMENT.md](PRODUCT_REQUIREMENT_DOCUMENT.md)
