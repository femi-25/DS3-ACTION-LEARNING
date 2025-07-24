import streamlit as st
import joblib
import numpy as np
import shap
from fairlearn.metrics import MetricFrame, demographic_parity_difference, equalized_odds_difference
from sklearn.metrics import accuracy_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------
# Load Data
# -------------------------------
try:
    X_test = np.load(r"C:\Users\srava\Desktop\Modelling task\data\X_test.npy")
    y_test = np.load(r"C:\Users\srava\Desktop\Modelling task\data\y_test.npy")
    sensitive_attr = np.load(r"C:\Users\srava\Desktop\Modelling task\data\sensitive_attr.npy")
except FileNotFoundError:
    st.warning("Data files not found! Using dummy data.")
    X_test = np.random.rand(100, 11)
    y_test = np.random.randint(0, 2, 100)
    sensitive_attr = np.random.randint(0, 2, 100)

# -------------------------------
# Load Predictions (Pre-Saved for RF, NN, GNN)
# -------------------------------
y_pred_xgb = np.load(r"C:\Users\srava\Desktop\Modelling task\y_pred_xgboost.npy")
y_pred_rf = np.load(r"C:\Users\srava\Desktop\Modelling task\y_pred_rf.npy")
y_pred_nn = np.load(r"C:\Users\srava\Desktop\Modelling task\y_pred_nn.npy")
y_pred_gnn = np.load(r"C:\Users\srava\Desktop\Modelling task\y_pred_gnn.npy")

# -------------------------------
# Streamlit UI
# -------------------------------
st.title("Fairness & Explainability Dashboard ")

model_choice = st.selectbox("Select Model", ["XGBoost", "Random Forest", "Neural Network", "GNN"])

# -------------------------------
# Fairness Metrics
# -------------------------------
st.header("Fairness Evaluation")

if model_choice == "XGBoost":
    y_pred = y_pred_xgb
elif model_choice == "Random Forest":
    y_pred = y_pred_rf
elif model_choice == "Neural Network":
    y_pred = y_pred_nn
elif model_choice == "GNN":
    y_pred = y_pred_gnn

if model_choice != "GNN":
    metric_frame = MetricFrame(metrics={"Accuracy": accuracy_score},
                               y_true=y_test, y_pred=y_pred,
                               sensitive_features=sensitive_attr)

    st.subheader("Group-wise Accuracy (Fairlearn MetricFrame)")
    st.table(metric_frame.by_group)

    dpd = demographic_parity_difference(y_test, y_pred, sensitive_features=sensitive_attr)
    eod = equalized_odds_difference(y_test, y_pred, sensitive_features=sensitive_attr)

    st.metric("Demographic Parity Difference", round(dpd, 3))
    st.metric("Equalized Odds Difference", round(eod, 3))

else:
    st.subheader("Group-wise MAE (GNN)")

    mae_frame = MetricFrame(
        metrics={"MAE": mean_absolute_error},
        y_true=y_test,
        y_pred=y_pred,
        sensitive_features=sensitive_attr
    )
    st.table(mae_frame.by_group)

# -------------------------------
# Explainability - SHAP for XGBoost
# -------------------------------
st.header("Explainability ")

features = [
    "Overall", "Potential", "Age", "Height_cm", "Weight_kg",
    "Pace", "Shooting", "Passing", "Dribbling", "Defending", "Physical"
]

if model_choice == "XGBoost":
    st.subheader("SHAP Summary for XGBoost")

    model = joblib.load("models/xgboost_model.pkl")

    expected_features = model.get_booster().num_features()
    if X_test.shape[1] < expected_features:
        padding = np.zeros((X_test.shape[0], expected_features - X_test.shape[1]))
        X_test_fixed = np.concatenate([X_test, padding], axis=1)
    else:
        X_test_fixed = X_test

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test_fixed)

    fig, ax = plt.subplots()
    shap.summary_plot(shap_values, X_test_fixed, feature_names=features, show=False)
    st.pyplot(fig)

else:
    st.subheader(f"Feature Importance for {model_choice} ")
    importance = np.random.rand(len(features))
    fig, ax = plt.subplots()
    sns.barplot(x=importance, y=features, ax=ax)
    
    ax.set_title(f"{model_choice} - Feature Importance (Placeholder)")
    st.pyplot(fig)

# -------------------------------
# Raw Predictions Display
# -------------------------------
st.header("Raw Model Predictions Output")

if model_choice == "XGBoost":
    st.subheader("XGBoost Predictions (Pre-Saved)")
    st.write(y_pred_xgb)

elif model_choice == "Random Forest":
    st.subheader("Random Forest Predictions (Pre-Saved)")
    st.write(y_pred_rf)

elif model_choice == "Neural Network":
    st.subheader("Neural Network Predictions (Pre-Saved)")
    st.write(y_pred_nn)

elif model_choice == "GNN":
    st.subheader("GNN Predictions (Pre-Saved)")
    st.write(y_pred_gnn)
