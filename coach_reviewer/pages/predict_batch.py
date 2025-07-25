import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="Batch Player Prediction", page_icon="📄")

st.title("Player Prediction (Batch CSV)")

ENDPOINT = "/predict"
base_url = st.session_state.get("base_url", "http://localhost:8000")
url = base_url + ENDPOINT

uploaded_file = st.file_uploader("Upload player CSV", type="csv")
if not uploaded_file:
    st.info("👆 Upload a CSV file with player features to begin.")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.subheader("Preview of Uploaded Data")
        st.dataframe(df.head())

        # Send to API
        response = requests.post(url, json={"features": df.to_dict(orient="records")})
        if response.status_code == 200:
            predictions = response.json()
            scores = [r["predicted_overall"] for r in predictions]
            df["predicted_overall"] = scores
            st.success("✅ Batch prediction completed")
            st.dataframe(df)
        else:
            st.error("❌ API call failed")
            st.text(f"Status Code: {response.status_code}")
    except Exception as e:
        st.error(f"Upload or Prediction Error: {e}")