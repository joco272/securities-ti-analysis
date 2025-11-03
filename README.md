# Securities Technical Analysis Application

A comprehensive securities analysis and backtesting application for tracking and analyzing NYSE securities with technical indicators.

## Overview

This application empowers users to make data-driven investment decisions by providing:
- Technical indicator calculation and storage
- Interactive data visualization
- Strategy backtesting capabilities
- Portfolio tracking and watchlist management

## Key Features

### Technical Indicators
The application calculates and stores multiple technical indicators:

**Priority Indicators (MVP Phase 1):**
- **MACD** (Moving Average Convergence Divergence): Trend-following momentum indicator
- **RSI** (Relative Strength Index): Momentum oscillator (14-period default)
- **MFI** (Money Flow Index): Volume-weighted RSI

**Additional Indicators:**
- Stochastic RSI: Enhanced RSI for sensitive momentum readings
- A/D (Accumulation/Distribution Line): Volume-based money flow indicator
- OBV (On-Balance Volume): Cumulative volume-based momentum
- SMA (Simple Moving Averages): 50 and 200-period trend indicators
- AO (Awesome Oscillator): Momentum indicator

### Time Intervals
Supports multiple time intervals for analysis:
- 15-minute (15m)
- 1-hour (1h)
- 4-hour (4h)
- 1-day (1d)

### Backtesting
Evaluate trading strategies with key performance metrics:
- **Sharpe Ratio**: Risk-adjusted return measurement
- **Win Rate (%)**: Percentage of profitable trades

**Initial Strategy:**
- RSI Oscillator Strategy with configurable buy/sell thresholds (default: 30/70)

### Portfolio Management
- Track holdings and transactions
- Create and manage multiple watchlists
- View portfolio summary with unrealized P&L

## Technology Stack

- **Backend**: FastAPI
- **Data Processing**: Pandas, NumPy, TA-Lib, pandas-ta
- **Database**: SQLite (local storage in `securities_data.db`)
- **Machine Learning**: scikit-learn, backtesting.py
- **Frontend**: Streamlit
- **Visualization**: Plotly
- **Data Source**: yfinance

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/joco272/securities-ti-analysis.git
cd securities-ti-analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Note: TA-Lib may require additional system-level installation. See [TA-Lib Installation Guide](https://github.com/mrjbq7/ta-lib#installation) for platform-specific instructions.

## Usage

### Running the Application

Start the Streamlit application:
```bash
streamlit run src/app.py
```

The application will open in your default web browser.

### Basic Workflow

1. **Enter Analysis Parameters** (sidebar):
   - Stock ticker (e.g., AAPL, MSFT)
   - Time interval (15m, 1h, 4h, 1d)
   - Date range

2. **Select Indicators** to display on charts

3. **Fetch, Store, and Analyze** to:
   - Download historical data from yfinance
   - Calculate technical indicators
   - Store data in SQLite database
   - Display interactive charts
   - Run backtesting analysis

4. **Manage Portfolio**:
   - Add transactions via the Transaction Log section
   - View portfolio summary with current holdings
   - Create watchlists for tracking securities

## Project Structure

```
securities-ti-analysis/
├── config/
│   └── settings.py          # Configuration settings
├── src/
│   ├── app.py              # Main Streamlit application
│   ├── database.py         # Database initialization
│   ├── data_processing/
│   │   ├── indicators.py   # Technical indicator calculations
│   │   ├── data_retrieval.py
│   │   ├── data_storage.py
│   │   └── data_query.py
│   ├── ml_models/
│   │   └── backtesting_framework.py  # Backtesting strategies
│   ├── portfolio/
│   │   ├── summary.py      # Portfolio summary logic
│   │   ├── transaction.py  # Transaction management
│   │   └── watchlist.py    # Watchlist management
│   └── plotting/
│       └── charts.py       # Chart visualization
├── tests/
├── requirements.txt
├── PRODUCT_REQUIREMENT_DOCUMENT.md
└── README.md
```

## Configuration

### Developer Configuration
Currently, configuration is done through code editing:
- Add indicators: Edit `src/data_processing/indicators.py`
- Database settings: Edit `config/settings.py`
- Strategy parameters: Edit `src/ml_models/backtesting_framework.py`

A user-facing configuration UI is planned for future releases.

## Development Phases

### Phase 1 (MVP - Current)
- ✅ Core technical indicators (MACD, RSI, MFI)
- ✅ Additional indicators (Stochastic RSI, A/D, OBV, SMA, AO)
- ✅ Basic backtesting with Sharpe ratio and win rate
- ✅ SQLite data storage
- ✅ Streamlit UI with Plotly charts
- ✅ Portfolio tracking and watchlist management

### Phase 2 (Planned)
- Enhanced backtesting metrics (drawdown, Sortino ratio)
- Real-time data integration
- Automated indicator updates
- Additional technical indicators

### Phase 3 (Future)
- Machine learning predictive models
- News aggregation with sentiment analysis
- User-configurable indicators via UI
- Multi-user support

## Data Management

- Historical data is fetched from yfinance on-demand
- Calculated indicators are stored in SQLite (`securities_data.db`)
- Data persists across application sessions
- Manual refresh via UI button

## Contributing

This is a personal project. For questions or suggestions, please open an issue on GitHub.

## License

[Add your license information here]

## Acknowledgments

- [TA-Lib](https://github.com/mrjbq7/ta-lib) for technical analysis functions
- [pandas-ta](https://github.com/twopirllc/pandas-ta) for additional indicators
- [backtesting.py](https://kernc.github.io/backtesting.py/) for backtesting framework
- [Streamlit](https://streamlit.io/) for the web framework
- [Plotly](https://plotly.com/) for interactive charts

## References

For detailed project requirements and specifications, see [PRODUCT_REQUIREMENT_DOCUMENT.md](PRODUCT_REQUIREMENT_DOCUMENT.md).
