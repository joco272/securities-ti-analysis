from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processing.data_retrieval import fetch_ohlcv
from data_processing.indicators import calculate_indicators

class RsiOscillator(Strategy):
    """
    A simple RSI-based trading strategy.
    """
    upper_bound = 70
    lower_bound = 30
    rsi_window = 14

    def init(self):
        # The backtesting library will automatically use the 'rsi' column
        # from the data passed to the Backtest instance.
        pass

    def next(self):
        if crossover(self.data.rsi, self.upper_bound):
            self.position.close()
        elif crossover(self.lower_bound, self.data.rsi):
            self.buy()

def run_backtest(data: pd.DataFrame):
    """
    Runs a backtest on the given data and returns the results.
    """
    bt = Backtest(data, RsiOscillator, cash=10000, commission=.002)
    stats = bt.run()
    return stats

if __name__ == '__main__':
    ticker = 'AAPL'
    start_date = '2020-01-01'
    end_date = '2023-12-31'
    interval = '1d'

    try:
        # 1. Fetch data
        ohlcv_data = fetch_ohlcv(ticker, start_date, end_date, interval)
        if ohlcv_data.empty:
            print(f"No data found for {ticker}.")
        else:
            # 2. Calculate indicators
            data_with_indicators = calculate_indicators(ohlcv_data)

            # 3. Run backtest
            results = run_backtest(data_with_indicators.dropna())

            # 4. Print results
            print("Backtest Results:")
            print(f"Sharpe Ratio: {results['Sharpe Ratio']}")
            print(f"Win Rate [%]: {results['Win Rate [%]']}")

    except Exception as e:
        print(f"An error occurred during backtesting: {e}")
