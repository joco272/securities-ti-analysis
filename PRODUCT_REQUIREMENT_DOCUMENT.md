# Product Requirement Document: Securities Analysis and News Aggregator

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
*   **Initial Scope:**
    *   **Indicators:** MACD, MFI, RSI
    *   **Intervals:** 15-minute, 45-minute, 4-hour
*   **Note on Intervals:** The `yfinance` library directly supports 15-minute data. However, 45-minute and 4-hour intervals are not natively supported and will be implemented by fetching higher-resolution data (15-minute for 45-minute intervals, 1-hour for 4-hour intervals) and resampling it to the desired timeframes.
*   **Technical Details:**
    *   The application will use the TA-Lib library for indicator calculations.
    *   Indicator data will be stored in a local SQLite database file (`securities_data.db`).

### 4.2. Machine Learning Models for Buy/Sell Signals

*   **Description:** The application will allow users to backtest machine learning-based trading strategies against historical data.
*   **User Stories:**
    *   As a user, I want to be able to backtest a trading strategy to evaluate its performance.
    *   As a user, I want to see key performance metrics for my backtested strategies.
*   **Initial Scope:**
    *   **Backtesting Metrics:** Sharpe ratio, win/loss ratio
*   **Technical Details:**
    *   The application will use the `scikit-learn` and `backtesting.py` libraries for backtesting.

### 4.3. Customization

*   **Description:** Users will be able to add new technical indicators and time intervals to the application.
*   **Initial Implementation:** In the MVP, new indicators and intervals are configured in the `config/intervals.py` file. Developers can add new intervals by modifying the `INTERVAL_CONFIG` dictionary, specifying the source interval to fetch from yfinance and the resampling rule if needed.
*   **Example Configuration:**
    ```python
    '45m': {
        'source_interval': '15m',  # Fetch 15-minute data
        'resample_rule': '45min',  # Resample to 45-minute intervals
        'description': '45-minute intervals (resampled from 15m)'
    }
    ```
*   **Future Enhancement:** A user-facing UI for adding and configuring intervals and indicators is planned for a future release, allowing non-technical users to customize the application without editing configuration files.

## 5. Technology Stack

*   **Backend:** FastAPI
*   **Data Processing:** Pandas, NumPy, TA-Lib
 *   **Database:** SQLite (for local data storage)
*   **Machine Learning:** scikit-learn, backtesting.py
*   **Frontend:** Streamlit
*   **Data Source:** yfinance (initially), with the ability to add other sources like finnhub, polygon.io, or alphavantage.

## 6. Deployment

*   **Initial Deployment:** The application will be deployed on a Windows 11 PC.
*   **Future Deployment:** The application will be containerized (e.g., using Docker) for easier deployment and scalability.
