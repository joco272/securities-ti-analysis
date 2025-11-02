import pandas as pd
import vectorbt as vbt

def run_backtest(price_data: pd.DataFrame, entry_signals: pd.Series, exit_signals: pd.Series):
    """
    Runs a backtest using the vectorbt library.

    Args:
        price_data: DataFrame with at least a 'Close' column for the price.
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
        price_data['Close'],
        entries=entry_signals,
        exits=exit_signals,
        freq='1D' # Assuming daily frequency, adjust if necessary
    )

    # --- Calculate Performance Metrics ---
    stats = portfolio.stats()
    sharpe_ratio = stats.get('Sharpe Ratio')
    win_rate = stats.get('Win Rate [%]')
    total_return = stats.get('Total Return [%]')
    num_trades = stats.get('Total Trades')

    # --- Generate the Plot ---
    plot = portfolio.plot()

    return {
        "Sharpe Ratio": sharpe_ratio,
        "Win Rate [%]": win_rate,
        "Total Return [%]": total_return,
        "# Trades": num_trades
    }, plot
