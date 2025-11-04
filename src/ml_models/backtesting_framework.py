import vectorbt as vbt
import pandas as pd

def run_backtest(data: pd.DataFrame, indicator: str, lower_bound: int, upper_bound: int):
    """
    Runs a backtest using vectorbt based on a selected indicator and bounds.

    Args:
        data: DataFrame with OHLCV data and indicator columns.
        indicator: The name of the indicator column to use (e.g., 'rsi', 'mfi').
        lower_bound: The lower bound for the buy signal.
        upper_bound: The upper bound for the sell signal.

    Returns:
        A dictionary with key backtesting stats.
    """
    if indicator not in data.columns:
        raise ValueError(f"Dataframe must contain an '{indicator}' column for backtesting.")

    # --- 1. Define Entry and Exit Signals ---
    entries = data[indicator] < lower_bound
    exits = data[indicator] > upper_bound

    # --- 2. Run the Portfolio Simulation ---
    portfolio = vbt.Portfolio.from_signals(
        close=data['close'],
        entries=entries,
        exits=exits,
        init_cash=10000,
        fees=0.002, # 0.2% commission
        freq='D' # Assume daily frequency for now
    )

    # --- 3. Extract and Return Key Statistics ---
    stats = portfolio.stats()

    return {
        "Sharpe Ratio": stats['Sharpe Ratio'],
        "Win Rate [%]": stats['Win Rate [%]']
    }

if __name__ == '__main__':
    print("This module is intended to be used by the main application.")
    print("To test, run the main app and trigger an analysis which will then call this backtesting framework.")
