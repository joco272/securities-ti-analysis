from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd

class RsiOscillator(Strategy):
    """
    A simple RSI-based trading strategy.
    It buys when RSI crosses below the lower bound and sells when it crosses above the upper bound.
    """
    upper_bound = 70
    lower_bound = 30

    def init(self):
        # The backtesting library automatically uses the column named 'rsi' from the data feed.
        pass

    def next(self):
        if crossover(self.data.rsi, self.upper_bound):
            self.position.close()
        elif crossover(self.lower_bound, self.data.rsi):
            self.buy()

def run_backtest(data: pd.DataFrame):
    """
    Runs a backtest on the given data, which must contain OHLCV and 'rsi' columns.
    The column names for OHLCV must be capitalized: 'Open', 'High', 'Low', 'Close', 'Volume'.
    
    Returns:
        stats: Backtest statistics including Sharpe Ratio and Win/Loss Ratio
    """
    # The backtesting library requires capitalized column names for OHLCV.
    data_for_backtest = data.copy()
    data_for_backtest.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }, inplace=True)

    bt = Backtest(data_for_backtest, RsiOscillator, cash=10000, commission=.002)
    stats = bt.run()
    
    # Calculate win/loss ratio from trades
    # Check if '_trades' key exists to avoid issues with library changes
    if '_trades' in stats:
        trades = stats['_trades']
        if not trades.empty:
            winning_trades = len(trades[trades['PnL'] > 0])
            losing_trades = len(trades[trades['PnL'] < 0])
            
            if losing_trades > 0:
                win_loss_ratio = winning_trades / losing_trades
            elif winning_trades > 0:
                win_loss_ratio = float('inf')  # All trades are winners
            else:
                win_loss_ratio = float('nan')  # All trades are breakeven
        else:
            win_loss_ratio = float('nan')  # No trades executed
    else:
        # Fallback if trades data is not available
        win_loss_ratio = float('nan')
    
    # Add the win/loss ratio to the stats
    stats['Win/Loss Ratio'] = win_loss_ratio
    
    return stats

if __name__ == '__main__':
    # This block is for demonstrating the backtesting framework.
    # In the main app, the data is fetched and reconstructed from the database.

    # This is a placeholder for a direct data fetch for testing purposes.
    # A real test would pull from a saved file or a small, self-contained dataset.
    print("This module is intended to be used by the main application.")
    print("To test, run the main app and trigger the analysis.")
