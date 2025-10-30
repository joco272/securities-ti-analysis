import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os

def train_and_save_model(X: pd.DataFrame, y: pd.Series, model_path: str):
    """
    Trains a RandomForestClassifier model and saves it to a file.

    Args:
        X: DataFrame of features.
        y: Series of target signals.
        model_path: The path where the trained model will be saved.

    Returns:
        The accuracy of the trained model on the test set.
    """
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Initialize and train the model
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # Ensure the directory for the model path exists
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    # Save the trained model to a file
    joblib.dump(model, model_path)

    print(f"Model trained and saved to {model_path}")
    return accuracy

def load_model(model_path: str):
    """
    Loads a trained model from a file.
    """
    if not os.path.exists(model_path):
        return None
    model = joblib.load(model_path)
    return model

def predict_signal(model, data_point: pd.DataFrame):
    """
    Uses a trained model to predict a signal for a single new data point.
    """
    # The model expects a 2D array, so we reshape the single row
    return model.predict(data_point)[0]


if __name__ == '__main__':
    # --- Test block for model training and management ---
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from data_processing.data_query import fetch_data_with_indicators
    from feature_engineering import prepare_data_for_ml

    ticker_to_test = "MSFT"
    interval_to_test = "1d"
    model_save_path = f"models/{ticker_to_test}_{interval_to_test}_model.joblib"

    print("--- Testing Model Training, Saving, Loading, and Prediction ---")

    # 1. Get data
    df = fetch_data_with_indicators(ticker_to_test, interval_to_test)
    if df.empty:
        raise Exception("No data found to test model training.")

    # 2. Prepare data for ML
    X, y = prepare_data_for_ml(df)

    # 3. Train and save the model
    accuracy = train_and_save_model(X, y, model_save_path)
    print(f"Model accuracy on test set: {accuracy:.2f}")

    # 4. Load the model
    loaded_model = load_model(model_save_path)
    if loaded_model:
        print(f"\nModel successfully loaded from {model_save_path}")
    else:
        raise Exception("Failed to load the model.")

    # 5. Test prediction on a single data point
    sample_data_point = X.iloc[[-1]] # Get the last row as a DataFrame
    prediction = predict_signal(loaded_model, sample_data_point)
    print(f"\nPrediction for the last data point: {prediction}")
    print(f" (1=Buy, -1=Sell, 0=Hold)")

    print("\nTest complete.")
