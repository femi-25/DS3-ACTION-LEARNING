import streamlit as st
import pandas as pd
import requests
from fairlearn.metrics import MetricFrame, demographic_parity_difference, equalized_odds_difference
from sklearn.metrics import accuracy_score
import seaborn as sns
import matplotlib.pyplot as plt

API_URL = "http://localhost:8000"

st.title("⚖️ Fairness Evaluation Dashboard")

# Call FastAPI to fetch prediction results
if st.button("📥 Fetch and Analyze Predictions"):
    try:
        response = requests.get(f"{API_URL}/predictions_with_sensitive_features")
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)

            if {"y_true", "y_pred_baseline", "y_pred_fair", "gender"}.issubset(df.columns):

                # Fairlearn metrics
                metric_frame_baseline = MetricFrame(
                    metrics={"accuracy": accuracy_score},
                    y_true=df["y_true"],
                    y_pred=df["y_pred_baseline"],
                    sensitive_features=df["gender"]
                )

                metric_frame_fair = MetricFrame(
                    metrics={"accuracy": accuracy_score},
                    y_true=df["y_true"],
                    y_pred=df["y_pred_fair"],
                    sensitive_features=df["gender"]
                )

                # Group accuracies
                st.subheader("📊 Accuracy by Gender Group")
                st.write("**Baseline Model**")
                st.dataframe(metric_frame_baseline.by_group)

                st.write("**Fairness-Aware Model**")
                st.dataframe(metric_frame_fair.by_group)

                # Parity metrics
                dp_baseline = demographic_parity_difference(
                    df["y_true"], df["y_pred_baseline"], sensitive_features=df["gender"])
                dp_fair = demographic_parity_difference(
                    df["y_true"], df["y_pred_fair"], sensitive_features=df["gender"])

                eo_baseline = equalized_odds_difference(
                    df["y_true"], df["y_pred_baseline"], sensitive_features=df["gender"])
                eo_fair = equalized_odds_difference(
                    df["y_true"], df["y_pred_fair"], sensitive_features=df["gender"])

                st.subheader("📏 Fairness Metrics")
                fairness_metrics = pd.DataFrame({
                    "Model": ["Baseline", "Fairness-Aware"],
                    "Demographic Parity Difference": [dp_baseline, dp_fair],
                    "Equalized Odds Difference": [eo_baseline, eo_fair]
                })
                st.dataframe(fairness_metrics)

                # Plot (optional)
                st.subheader("📉 Accuracy Comparison")
                fig, ax = plt.subplots()
                metric_frame_baseline.by_group.plot(kind="bar", ax=ax, label="Baseline", color="skyblue")
                metric_frame_fair.by_group.plot(kind="bar", ax=ax, label="Fair", color="green", alpha=0.6)
                plt.legend()
                st.pyplot(fig)

            else:
                st.error("Missing required columns in response.")
        else:
            st.error("Failed to fetch data from API.")
    except Exception as e:
        st.error(f"Error: {e}")
