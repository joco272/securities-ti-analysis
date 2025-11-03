# Product Requirement Document: Securities Analysis and News Aggregator

## Document Summary

This PRD addresses the following key decisions for the MVP:

1. **Initial Indicators**: MACD, RSI, and MFI are the priority indicators for Phase 1, with additional indicators (Stochastic RSI, A/D, OBV, SMA, AO) already implemented for enhanced analysis capabilities.

2. **Backtesting Metrics**: Sharpe ratio and win rate (%) are the primary metrics for evaluating strategy performance, with additional metrics planned for future releases.

3. **Technology Stack**: The stack consists of FastAPI, Pandas, NumPy, TA-Lib, pandas-ta, SQLite, scikit-learn, backtesting.py, Streamlit, and Plotly - all Python-based open-source technologies suitable for Windows 11 deployment.

4. **Configuration Approach**: Developer-led configuration initially (editing code/config files), with user-facing configuration UI planned for future releases.

## 1. Introduction

This document outlines the product requirements for a securities analysis and news aggregator application. The application is designed for a user who wants to track and analyze securities, develop and backtest trading strategies, and stay informed about market news.

## 2. Vision and Goals

The vision is to create a comprehensive and customizable tool that empowers users to make data-driven investment decisions. The initial goal is to build a minimum viable product (MVP) that focuses on the core features of technical indicator calculation, storage, and machine learning-based backtesting.

## 3. User Personas

The primary user persona is a technically proficient individual who is actively involved in the stock market. This user is comfortable with financial concepts and is looking for a powerful tool to enhance their trading strategies.

## 4. Feature Requirements

### 4.1. Core Technical Indicator Calculation and Storage

*   **Description:** The application will calculate and store a variety of technical indicators for securities trading on the NYSE.
*   **User Stories:**
    *   As a user, I want to be able to calculate and store technical indicators for any security on the NYSE.
    *   As a user, I want the application to automatically update the technical indicators at the close of each time interval.
*   **Initial Scope (Priority Indicators):**
    *   **Primary Indicators (MVP Phase 1):** MACD, RSI, MFI
        *   These three indicators form the core of the initial release and are essential for basic technical analysis.
        *   MACD (Moving Average Convergence Divergence): Trend-following momentum indicator
        *   RSI (Relative Strength Index): Momentum oscillator measuring speed and magnitude of price changes
        *   MFI (Money Flow Index): Volume-weighted RSI that identifies overbought/oversold conditions
    *   **Additional Indicators (Implemented):** 
        *   Stochastic RSI: Enhanced RSI for more sensitive momentum readings
        *   A/D (Accumulation/Distribution Line): Volume-based indicator showing money flow
        *   OBV (On-Balance Volume): Cumulative volume-based momentum indicator
        *   SMA (Simple Moving Averages): 50-period and 200-period moving averages for trend identification
        *   AO (Awesome Oscillator): Momentum indicator using pandas-ta library
    *   **Time Intervals:** 15-minute (15m), 1-hour (1h), 4-hour (4h), 1-day (1d)
*   **Note on Intervals:** The '45m' interval is not supported by the `yfinance` library. A potential workaround is to resample 15-minute data to 45-minute intervals. This will be considered for a future release.
*   **Technical Details:**
    *   The application uses the TA-Lib library for most indicator calculations.
    *   The pandas-ta library is used for indicators not available in TA-Lib (e.g., Awesome Oscillator).
    *   Indicator data will be stored in a local SQLite database file (`securities_data.db`).
    *   All OHLCV (Open, High, Low, Close, Volume) data is stored alongside calculated indicators for historical analysis.

### 4.2. Machine Learning Models for Buy/Sell Signals

*   **Description:** The application will allow users to backtest machine learning-based trading strategies against historical data.
*   **User Stories:**
    *   As a user, I want to be able to backtest a trading strategy to evaluate its performance.
    *   As a user, I want to see key performance metrics for my backtested strategies.
    *   As a user, I want to understand both profitability and risk-adjusted returns of my strategies.
*   **Initial Scope:**
    *   **Key Performance Metrics:**
        *   **Sharpe Ratio**: Risk-adjusted return metric measuring excess return per unit of risk (volatility). Higher values indicate better risk-adjusted performance.
        *   **Win Rate (%)**: Percentage of profitable trades relative to total number of trades. Provides insight into strategy consistency.
    *   **Future Metrics (Planned):**
        *   Total Return/Profit & Loss
        *   Maximum Drawdown
        *   Sortino Ratio
        *   Calmar Ratio
        *   Average Win/Loss
*   **Initial Strategy:**
    *   **RSI Oscillator Strategy**: A momentum-based strategy using RSI indicator
        *   Buy signal: RSI crosses below 30 (oversold condition)
        *   Sell signal: RSI crosses above 70 (overbought condition)
        *   Default parameters: 70/30 thresholds, configurable for optimization
*   **Technical Details:**
    *   The application uses the `backtesting.py` library for strategy backtesting framework.
    *   The `scikit-learn` library is available for future machine learning model integration.
    *   Initial cash: $10,000 (configurable)
    *   Commission: 0.2% per trade (configurable)

### 4.3. Customization (Future Scope)

*   **Description:** Users will be able to add new technical indicators and time intervals to the application.
*   **Initial Implementation:** In the MVP, new indicators and intervals will be added by a developer editing a configuration file. A user-facing UI for this feature is planned for a future release.

## 5. Technology Stack

The following technology stack has been selected based on the requirements for data processing, analysis, visualization, and deployment:

*   **Backend Framework:** FastAPI
    *   RESTful API framework for potential future API endpoints
    *   Fast, modern, and Python-based
*   **Data Processing:** Pandas, NumPy, TA-Lib, pandas-ta
    *   Pandas: Core data manipulation and time-series analysis
    *   NumPy: Numerical computing and array operations
    *   TA-Lib: Technical analysis library for standard indicators (MACD, RSI, MFI, etc.)
    *   pandas-ta: Additional technical analysis indicators (Awesome Oscillator, etc.)
*   **Database:** SQLite (for local data storage)
    *   Lightweight, file-based database requiring no separate server
    *   Ideal for single-user desktop application
    *   Database file: `securities_data.db`
*   **Machine Learning & Backtesting:** scikit-learn, backtesting.py
    *   scikit-learn: Machine learning library for future predictive models
    *   backtesting.py: Specialized library for strategy backtesting with built-in metrics
*   **Frontend:** Streamlit
    *   Python-based web framework for rapid dashboard development
    *   Interactive UI without JavaScript/HTML complexity
    *   Real-time data visualization and user interaction
*   **Data Visualization:** Plotly
    *   Interactive charting library for technical analysis
    *   Multi-pane charts for price and indicators
    *   Supports candlestick charts, line charts, and volume bars
*   **Data Sources:** 
    *   Primary: yfinance (free, comprehensive historical data for NYSE securities)
    *   Future integration: finnhub, polygon.io, or alphavantage for real-time data and additional markets

**Technology Stack Rationale:**
*   All technologies are open-source and freely available
*   Python-based stack ensures consistency and ease of integration
*   Proven libraries with active community support
*   Suitable for Windows 11 deployment environment

## 6. Deployment

*   **Initial Deployment:** The application will be deployed on a Windows 11 PC.
*   **Future Deployment:** The application will be containerized (e.g., using Docker) for easier deployment and scalability.

## 7. Development Approach

### 7.1. Phased Implementation
The project follows a phased approach to manage scope and deliver value incrementally:

*   **Phase 1 (MVP - Current):** 
    *   Core technical indicators (MACD, RSI, MFI)
    *   Basic backtesting with Sharpe ratio and win rate
    *   SQLite data storage
    *   Streamlit UI for visualization
    *   Portfolio tracking and watchlist management

*   **Phase 2 (Planned):**
    *   Additional technical indicators as needed
    *   Enhanced backtesting metrics (drawdown, Sortino ratio, etc.)
    *   Real-time data integration
    *   Automated indicator updates

*   **Phase 3 (Future):**
    *   Machine learning models for predictive analysis
    *   News aggregation and sentiment analysis
    *   User-configurable indicators via UI
    *   Multi-user support and authentication

### 7.2. Configuration Management
*   **Initial Approach:** Developer-led configuration through code and configuration files
    *   New indicators added by editing `indicators.py`
    *   Time intervals configured in application code
    *   Database settings in `config/settings.py`
*   **Future Enhancement:** User-facing configuration UI (planned for later release)

### 7.3. Data Management
*   Historical data fetched from yfinance on-demand
*   Calculated indicators stored in SQLite for quick retrieval
*   Data is persistent across application sessions
*   Manual data refresh via UI button

## 8. Success Criteria

The MVP will be considered successful when:
*   Users can fetch and store OHLCV data for any NYSE security
*   MACD, RSI, and MFI indicators are accurately calculated and stored
*   Users can visualize price data and indicators in interactive charts
*   Users can backtest the RSI oscillator strategy and view Sharpe ratio and win rate
*   Users can track portfolio holdings and transactions
*   Users can create and manage watchlists
*   The application runs reliably on Windows 11 without crashes
*   Data persists correctly in SQLite database

## 9. Future Enhancements

Based on user feedback and evolving requirements, the following enhancements are considered for future releases:
*   Additional technical indicators (Bollinger Bands, Fibonacci retracements, etc.)
*   Custom strategy builder with visual workflow
*   Automated trading signal alerts (email/SMS notifications)
*   Multi-timeframe analysis
*   Correlation analysis between securities
*   News aggregation with sentiment analysis
*   PDF report generation for backtesting results
*   Export functionality (CSV, Excel)
*   Cloud deployment for remote access
*   Mobile application
