import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

# Define preprocessing
categorical_features = ["Team", "Sport", "Season"]
numerical_features = ["Age", "Height", "Weight", "Year"]

preprocessor = ColumnTransformer(transformers=[
    ("num", StandardScaler(), numerical_features),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
])

# Path to your saved model
MODEL_PATH = "final_nn_model.h5"

def preprocess_input(df: pd.DataFrame):
    df = df.copy()

    # Example preprocessing: adjust this based on your model
    if "Sex" in df.columns:
        df["Sex"] = df["Sex"].map({"M": 1, "F": 0})

    df = df[numerical_features + categorical_features + ["Sex"]]
    return preprocessor.fit_transform(df)  # Fit-transform for demonstration

def predict_from_model(records: list, model_name: str = "Baseline"):
    df = pd.DataFrame(records)
    if df.empty:
        return []

    try:
        X_processed = preprocess_input(df)
        model = load_model(MODEL_PATH)
        y_pred_proba = model.predict(X_processed)
        y_pred_label = (y_pred_proba > 0.5).astype(int)

        predictions = []
        for i, row in df.iterrows():
            predictions.append({
                "index": i,
                "input": row.to_dict(),
                "predicted_potential": "High" if y_pred_label[i][0] == 1 else "Low",
                "probability": float(y_pred_proba[i][0])
            })

        return predictions
    except Exception as e:
        return [{"error": str(e)}]
