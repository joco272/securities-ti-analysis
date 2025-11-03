# Securities Technical Indicator Analysis Application

A comprehensive securities analysis and trading platform that provides technical indicator calculation, machine learning-based backtesting, portfolio management, and watchlist tracking.

## Overview

This application is designed for traders and investors who want to:
- Track and analyze securities with technical indicators
- Backtest trading strategies using machine learning
- Manage portfolios and watchlists
- Store and query historical price and indicator data

## Features

### ✅ Implemented Features

#### Core Technical Indicators
- **MACD** (Moving Average Convergence Divergence)
- **RSI** (Relative Strength Index)
- **MFI** (Money Flow Index)
- **Stochastic RSI**
- **A/D** (Accumulation/Distribution)
- **OBV** (On-Balance Volume)
- **Awesome Oscillator**
- **Moving Averages** (SMA 50, SMA 200)

#### Time Intervals
- 15-minute
- 1-hour
- 4-hour
- 1-day

#### Data Management
- SQLite database for local storage
- Automatic calculation and storage of indicators
- Query and retrieve historical data with indicators
- OHLCV (Open, High, Low, Close, Volume) data storage

#### Portfolio Management
- Track buy/sell transactions
- Calculate portfolio holdings and P&L
- View current positions and unrealized gains/losses
- Transaction history by ticker

#### Watchlist Management
- Create multiple custom watchlists
- Add/remove securities to watchlists
- Organize securities by categories

#### Machine Learning & Backtesting
- RSI-based trading strategy implementation
- Backtesting framework using historical data
- Performance metrics (Sharpe ratio, win rate)
- Strategy evaluation and comparison

#### Visualization
- Multi-pane interactive charts using Plotly
- Price charts with technical indicators overlay
- MACD histogram and signal lines
- RSI, MFI, and other oscillators

### 🚧 Planned Features (Future Roadmap)

#### News Aggregation (Priority 4)
- Continuous news monitoring from multiple sources
- Entity recognition for companies and officers
- Keyword and event-type search
- Portfolio-based alerting
- Searchable news repository

#### Advanced Financial Data (Priority 3)
- Company financial statements (10-K, 10-Q, 8-K)
- Analyst metrics (P/E ratio, EPS, Market Cap, etc.)
- Advanced search by sector, metrics, and fundamentals
- Integration with SEC EDGAR API

#### Real-Time Updates
- Automated interval-based updates
- Near real-time indicator calculation during market hours
- Scheduled batch processing after market close

#### Additional ML Models
- General market models
- Security-specific models
- Custom strategy development framework
- Advanced backtesting capabilities

## Technology Stack

- **Frontend**: Streamlit (Python-based web UI)
- **Backend**: FastAPI (for future API services)
- **Database**: SQLite (local storage)
- **Data Processing**: Pandas, NumPy
- **Technical Analysis**: TA-Lib, pandas-ta
- **Machine Learning**: scikit-learn, backtesting.py
- **Data Source**: yfinance (Yahoo Finance)
- **Visualization**: Plotly
- **Platform**: Windows 11 (initial deployment)

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

2. Install required packages:
```bash
pip install -r requirements.txt
```

**Note for Windows 11**: TA-Lib requires additional system-level dependencies:
- Download and install Visual C++ build tools from Microsoft
- For pre-built binaries, visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
- Download the appropriate `.whl` file for your Python version (e.g., `TA_Lib‑0.4.XX‑cpXX‑cpXX‑win_amd64.whl`)
- Install with: `pip install <downloaded_whl_file>`
- For detailed instructions, see [TA-Lib installation guide](https://github.com/mrjbq7/ta-lib#installation)

3. Initialize the database:
```bash
python src/database.py
```

## Usage

### Running the Application

Start the Streamlit application:
```bash
streamlit run src/app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Basic Workflow

1. **Fetch and Analyze Data**:
   - Enter a stock ticker (e.g., AAPL)
   - Select time interval and date range
   - Choose technical indicators to display
   - Click "Fetch, Store, and Analyze"

2. **Manage Portfolio**:
   - Add buy/sell transactions in the Transaction Log section
   - View your current holdings in the Portfolio Summary
   - Track unrealized P&L for each position

3. **Create Watchlists**:
   - Create a new watchlist using the sidebar
   - Add tickers to watchlists
   - Organize securities by themes or strategies

4. **Review Backtesting Results**:
   - Automatic backtesting runs with each analysis
   - View Sharpe ratio and win rate metrics
   - Evaluate trading strategy performance

## Project Structure

```
securities-ti-analysis/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration settings
├── src/
│   ├── __init__.py
│   ├── app.py              # Main Streamlit application
│   ├── database.py         # Database initialization and connection
│   ├── data_processing/
│   │   ├── __init__.py
│   │   ├── data_retrieval.py    # Fetch OHLCV data from yfinance
│   │   ├── indicators.py        # Technical indicator calculations
│   │   ├── data_storage.py      # Store data in database
│   │   └── data_query.py        # Query data from database
│   ├── ml_models/
│   │   ├── __init__.py
│   │   └── backtesting_framework.py  # Strategy backtesting
│   ├── portfolio/
│   │   ├── __init__.py
│   │   ├── watchlist.py    # Watchlist management
│   │   ├── transaction.py  # Transaction tracking
│   │   └── summary.py      # Portfolio summary
│   └── plotting/
│       ├── __init__.py
│       └── charts.py       # Plotly chart generation
├── tests/
│   └── __init__.py
├── scripts/
│   └── __init__.py
├── requirements.txt
├── PRODUCT_REQUIREMENT_DOCUMENT.md
├── RESPONSE_TO_JULES.md
└── README.md
```

## Database Schema

The application uses SQLite with the following tables:

- **price_data**: OHLCV data for each ticker and interval
- **indicator_data**: Calculated technical indicators
- **watchlists**: User-created watchlists
- **watchlist_items**: Tickers in each watchlist
- **transactions**: Buy/sell transaction history

## Development Priorities

As outlined in the [RESPONSE_TO_JULES.md](RESPONSE_TO_JULES.md) document:

1. **Priority 1** (✅ Completed): Core technical indicator calculation and storage
2. **Priority 2** (✅ Completed): Machine learning models and backtesting
3. **Priority 3** (Planned): Company financial data and advanced search
4. **Priority 4** (Planned): News aggregation and alerting

## Contributing

This is a personal project currently under development. Contributions, suggestions, and feedback are welcome.

## Documentation

- [Product Requirement Document](PRODUCT_REQUIREMENT_DOCUMENT.md) - Detailed feature requirements and technical specifications
- [Response to Jules](RESPONSE_TO_JULES.md) - Clarifications on project priorities and technical decisions

## License

This project is currently proprietary. Contact the repository owner for licensing information.

## Contact

For questions or suggestions, please open an issue in the GitHub repository.

---

**Status**: Active Development  
**Last Updated**: November 3, 2024  
**Version**: 0.1.0 MVP
