import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

def train_and_save_model(X: pd.DataFrame, y: pd.Series, model_path: str):
    """
    Trains a RandomForestClassifier model and saves it to a file.

    Args:
        X: DataFrame of features.
        y: Series representing the target variable.
        model_path: The file path where the trained model will be saved.
    """
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Initialize and train the RandomForestClassifier
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight='balanced'
    )
    model.fit(X_train, y_train)

    # --- (Optional) Evaluate the model ---
    # y_pred = model.predict(X_test)
    # print(f"Model Accuracy: {accuracy_score(y_test, y_pred):.2f}")

    # --- Save the trained model ---
    # Ensure the directory exists
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

def load_model(model_path: str):
    """
    Loads a trained model from a file.

    Args:
        model_path: The file path of the model.

    Returns:
        The loaded model, or None if the file doesn't exist.
    """
    if os.path.exists(model_path):
        print(f"Loading model from {model_path}")
        return joblib.load(model_path)
    else:
        print(f"No model found at {model_path}")
        return None
