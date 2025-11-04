import vectorbt as vbt
import pandas as pd

def run_backtest(data: pd.DataFrame):
    """
    Runs an RSI-based backtest using vectorbt.

    Args:
        data: DataFrame with OHLCV data and an 'rsi' column.

    Returns:
        A dictionary with key backtesting stats.
    """
    if 'rsi' not in data.columns:
        raise ValueError("Dataframe must contain an 'rsi' column for backtesting.")

    # --- 1. Define Entry and Exit Signals ---
    # We use a simple RSI strategy: buy when RSI crosses below 30, sell when it crosses above 70.
    entries = data['rsi'] < 30
    exits = data['rsi'] > 70

    # --- 2. Run the Portfolio Simulation ---
    # `vbt.Portfolio.from_signals` is a powerful tool that simulates a portfolio based on entry/exit signals.
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

    # We return a simple dictionary to keep the interface consistent with the rest of the app
    return {
        "Sharpe Ratio": stats['Sharpe Ratio'],
        "Win Rate [%]": stats['Win Rate [%]']
    }

if __name__ == '__main__':
    # This module is meant to be imported, but we can provide a simple test case.
    # To run, you'd need a data source with 'close' and 'rsi' columns.
    print("This module is intended to be used by the main application.")
    print("To test, run the main app and trigger an analysis which will then call this backtesting framework.")
