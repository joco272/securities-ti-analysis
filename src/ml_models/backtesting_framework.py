import pandas as pd
import vectorbt as vbt

def run_backtest(price_data: pd.DataFrame, entry_signals: pd.Series, exit_signals: pd.Series):
    """
    Runs a backtest using the vectorbt library.

    Args:
        price_data: DataFrame with at least a 'close' column for the price.
        entry_signals: A boolean pandas Series indicating entry points (True to enter).
        exit_signals: A boolean pandas Series indicating exit points (True to exit).

    Returns:
        A tuple of (stats, plot):
        stats: A dictionary of performance metrics.
        plot: A Plotly Figure object of the backtest.
    """
    # Ensure the price_data index is a DatetimeIndex
    price_data.index = pd.to_datetime(price_data.index)

    # Run the portfolio simulation from the signals
    portfolio = vbt.Portfolio.from_signals(
        price_data['close'],
        entries=entry_signals,
        exits=exit_signals,
        freq='1D' # Assuming daily frequency, adjust if necessary
    )

    # --- Calculate Performance Metrics ---
    stats = portfolio.stats()
    sharpe_ratio = stats['Sharpe Ratio']
    win_rate = stats['Win Rate [%]']
    total_return = stats['Total Return [%]']
    num_trades = stats['Total Trades']

    # --- Generate the Plot ---
    plot = portfolio.plot()

    return {
        "Sharpe Ratio": sharpe_ratio,
        "Win Rate [%]": win_rate,
        "Total Return [%]": total_return,
        "# Trades": num_trades
    }, plot


if __name__ == '__main__':
    # --- Test block for the new vectorbt backtesting framework ---
    # To run this test, execute `python -m src.ml_models.backtesting_framework` from the project root.
    from ..data_processing.data_query import fetch_data_with_indicators

    ticker_to_test = "MSFT"
    interval_to_test = "1d"

    print(f"--- Testing vectorbt Backtesting Framework for {ticker_to_test} ---")

    # 1. Get data
    df = fetch_data_with_indicators(ticker_to_test, interval_to_test)
    if df.empty:
        raise Exception("No data found to test backtesting.")

    # 2. Generate some simple example signals (e.g., RSI crossover)
    rsi = df['rsi']
    entry_signals = (rsi < 30).shift(1, fill_value=False) # Enter on the day *after* RSI crosses below 30
    exit_signals = (rsi > 70).shift(1, fill_value=False)  # Exit on the day *after* RSI crosses above 70

    # 3. Run the backtest
    try:
        results, fig = run_backtest(df, entry_signals, exit_signals)

        print("\n--- vectorbt Backtest Results ---")
        print(results)

        # To view the plot, uncomment the line below
        # fig.show()
        print("\nPlot created. To view, uncomment 'fig.show()' in the test block.")

    except Exception as e:
        print(f"\nAn error occurred during backtest: {e}")

    print("\nTest complete.")
