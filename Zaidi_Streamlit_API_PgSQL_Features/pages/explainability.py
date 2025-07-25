import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.title("📊 Explainability Dashboard")
st.markdown("Visualizing SHAP-based explanations for model predictions.")

try:
    response = requests.get("http://localhost:8000/shap_explanations")
    response.raise_for_status()
    data = response.json()

    feature_names = data["feature_names"]
    global_shap_values = data["global_shap_values"]
    local_explanations = data["local_explanations"]

    # Global Explanation
    st.subheader("🌐 Global Feature Importance")
    fig, ax = plt.subplots()
    ax.barh(feature_names, global_shap_values)
    ax.set_xlabel("SHAP Value")
    ax.set_title("Global Feature Importance")
    st.pyplot(fig)

    # Local Explanation
    st.subheader("👤 Local Explanation for One Prediction")
    selected = st.selectbox("Select Prediction", list(range(len(local_explanations))))
    local_exp = local_explanations[selected]
    local_df = pd.DataFrame(local_exp.items(), columns=["Feature", "SHAP Value"])
    local_df = local_df.sort_values(by="SHAP Value", ascending=True)

    fig2, ax2 = plt.subplots()
    ax2.barh(local_df["Feature"], local_df["SHAP Value"])
    ax2.set_xlabel("SHAP Value")
    ax2.set_title("Local Feature Impact")
    st.pyplot(fig2)

except Exception as e:
    st.error(f"Failed to load SHAP explanations: {e}")
