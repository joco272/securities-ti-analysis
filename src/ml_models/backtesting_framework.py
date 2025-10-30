from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd


from .model import load_model

class MlStrategy(Strategy):
    """
    A backtesting strategy that uses a pre-trained machine learning model to make trading decisions.
    """
    model_path = None # This will be set before running the backtest

    def init(self):
        self.model = load_model(self.model_path)
        if self.model is None:
            raise Exception(f"Could not load model from {self.model_path}. Train the model first.")

        # Prepare the feature columns based on the model's expected features
        self.feature_columns = self.model.feature_names_in_

    def next(self):
        # Get the latest data point for the features the model expects
        latest_data = self.data.df.iloc[[-1]][self.feature_columns]

        # Get the prediction from the model
        signal = self.model.predict(latest_data)[0]

        if signal == 1: # Buy signal
            self.buy()
        elif signal == -1: # Sell signal
            self.position.close() # or self.sell() if shorting is desired

class RsiOscillator(Strategy):
    """
    A simple RSI-based trading strategy for comparison.
    """
    upper_bound = 70
    lower_bound = 30

    def init(self):
        pass

    def next(self):
        if crossover(self.data.rsi, self.upper_bound):
            self.position.close()
        elif crossover(self.lower_bound, self.data.rsi):
            self.buy()

def run_backtest(data: pd.DataFrame, strategy: Strategy = RsiOscillator, **kwargs):
    """
    Runs a backtest on the given data, which must contain OHLCV and 'rsi' columns.
    The column names for OHLCV must be capitalized: 'Open', 'High', 'Low', 'Close', 'Volume'.
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

    # Pass any extra keyword arguments (like model_path) to the strategy
    bt = Backtest(data_for_backtest, strategy, cash=10000, commission=.002)
    stats = bt.run(**kwargs)
    return stats

if __name__ == '__main__':
    # --- Test block for the ML backtesting strategy ---
    import sys
    import os
    # Add the project root to the python path to allow absolute imports
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from src.data_processing.data_query import fetch_data_with_indicators

    ticker_to_test = "MSFT"
    interval_to_test = "1d"
    model_path_for_test = f"models/{ticker_to_test}_{interval_to_test}_model.joblib"

    print(f"--- Testing ML Backtesting Strategy for {ticker_to_test} ---")

    # 1. Get data
    df = fetch_data_with_indicators(ticker_to_test, interval_to_test)
    if df.empty:
        raise Exception("No data found to test backtesting.")

    # 2. Run the backtest with the MlStrategy
    # We pass the model_path as a keyword argument to the strategy
    try:
        results = run_backtest(df.dropna(), strategy=MlStrategy, model_path=model_path_for_test)

        print("\n--- ML Backtest Results ---")
        print(f"Sharpe Ratio: {results['Sharpe Ratio']}")
        print(f"Win Rate [%]: {results['Win Rate [%]']}")
    except Exception as e:
        print(f"\nAn error occurred during ML backtest: {e}")
        print("This is expected if the model has not been trained yet.")

    print("\nTest complete.")
