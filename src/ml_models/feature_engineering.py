import pandas as pd
import numpy as np

def prepare_data_for_ml(df: pd.DataFrame, future_periods: int = 5, change_threshold: float = 0.02):
    """
    Prepares data for machine learning by creating features (X) and a target (y).

    Args:
        df: DataFrame with price data and technical indicators.
        future_periods: The number of future periods to look ahead to determine the outcome.
        change_threshold: The percentage change required to trigger a buy or sell signal.

    Returns:
        A tuple of (X, y):
        X: DataFrame of features (the indicators).
        y: Series of target signals (1 for buy, -1 for sell, 0 for hold).
    """

    # --- 1. Define Features (X) ---
    # We will use all available indicator columns as our features.
    # Exclude the core OHLCV data from the feature set.
    feature_cols = [
        'macd', 'macdsignal', 'macdhist', 'mfi', 'rsi', 'stoch_rsi_k',
        'stoch_rsi_d', 'ad', 'obv', 'sma50', 'sma200', 'ao'
    ]
    # Ensure all selected feature columns exist in the DataFrame
    features_present = [col for col in feature_cols if col in df.columns]
    X = df[features_present].copy()

    # --- 2. Define Target (y) ---
    # Calculate the percentage change in price 'future_periods' from now.
    df['future_change'] = df['close'].pct_change(periods=future_periods).shift(-future_periods)

    # Create the target signals based on the threshold
    # 1 for Buy (price will go up), -1 for Sell (price will go down), 0 for Hold
    conditions = [
        (df['future_change'] > change_threshold),
        (df['future_change'] < -change_threshold)
    ]
    choices = [1, -1]
    y = np.select(conditions, choices, default=0)

    # Convert y to a pandas Series with the same index as X
    y = pd.Series(y, index=X.index, name="signal")

    # --- 3. Clean Data ---
    # Remove any rows with NaN values that might remain in X or y
    # This is crucial for most ML models
    combined = X.join(y)
    combined.dropna(inplace=True)

    X = combined[features_present]
    y = combined["signal"]

    return X, y


if __name__ == '__main__':
    import sys
    import os
    # --- Test block for feature engineering ---
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from data_processing.data_query import fetch_data_with_indicators

    ticker_to_test = "MSFT"
    interval_to_test = "1d"

    print(f"Fetching data for {ticker_to_test} to test feature engineering...")
    test_df = fetch_data_with_indicators(ticker_to_test, interval_to_test)

    if not test_df.empty:
        print("Data fetched. Preparing data for ML...")
        X, y = prepare_data_for_ml(test_df)

        print("\n--- Features (X) ---")
        print(f"Shape: {X.shape}")
        print("Columns:", X.columns.tolist())
        print(X.tail())

        print("\n--- Target (y) ---")
        print(f"Shape: {y.shape}")
        print("Signal distribution:")
        print(y.value_counts())

    else:
        print("No data found to test.")

    print("\nTest complete.")
