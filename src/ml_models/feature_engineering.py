import pandas as pd
import numpy as np

def prepare_data_for_ml(df: pd.DataFrame):
    """
    Prepares the data for machine learning by creating features and a target variable.

    Args:
        df: DataFrame with price data and calculated technical indicators.

    Returns:
        A tuple of (X, y):
        X: A DataFrame of features.
        y: A Series representing the target variable.
    """
    df_ml = df.copy()

    # --- Feature Selection ---
    # Define the list of technical indicators to be used as features
    feature_cols = [
        'macd', 'macdsignal', 'macdhist', 'mfi', 'rsi',
        'stoch_rsi_k', 'stoch_rsi_d', 'ad', 'obv',
        'sma50', 'sma200', 'ao'
    ]

    # Ensure all selected feature columns exist in the DataFrame
    features_present = [col for col in feature_cols if col in df_ml.columns]
    X = df_ml[features_present]

    # --- Target Definition ---
    # The goal is to predict the direction of the price change in the next N days.
    # 1 for an increase (buy), -1 for a decrease (sell), 0 for no significant change.
    n_days_future = 5
    future_price = df_ml['close'].shift(-n_days_future)
    price_change_percent = (future_price - df_ml['close']) / df_ml['close'] * 100

    # Define thresholds for buy/sell signals
    buy_threshold = 1.0  # e.g., price increase of >1%
    sell_threshold = -1.0 # e.g., price decrease of >1%

    conditions = [
        (price_change_percent > buy_threshold),
        (price_change_percent < sell_threshold)
    ]
    choices = [1, -1] # 1 for Buy, -1 for Sell
    y = pd.Series(np.select(conditions, choices, default=0), index=df_ml.index)

    # --- Data Cleaning ---
    # Combine features and target for cleaning
    full_df = X.join(y.to_frame('target'))
    # Remove rows with NaN values that can result from indicator calculations or the target shift
    full_df.dropna(inplace=True)

    if full_df.empty:
        return pd.DataFrame(), pd.Series()

    X_clean = full_df[features_present]
    y_clean = full_df['target']

    return X_clean, y_clean
