import streamlit as st
import pandas as pd
import requests

API_URL = "http://localhost:8000"  # Adjust if hosted differently

st.title("🏋️‍♂️ Upload Athlete Dataset & Predict Potential")

uploaded_file = st.file_uploader("📂 Upload CSV File", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File uploaded successfully!")

    st.subheader("📊 Preview of Uploaded Data")
    st.dataframe(df.head())

    # EDA
    if "Sex" in df.columns:
        st.write("**Gender Distribution:**")
        st.bar_chart(df["Sex"].value_counts())

    if "Medal" in df.columns:
        st.write("**Medal Distribution:**")
        st.bar_chart(df["Medal"].value_counts())

    if "Sport" in df.columns:
        st.write("**Sports Count:**")
        st.bar_chart(df["Sport"].value_counts().head(10))

    # Model selection
    model_choice = st.selectbox("🤖 Choose prediction model:", ["Baseline Model", "Fairness-Aware Model"])

    if st.button("🚀 Run Prediction"):
        try:
            with st.spinner("Calling prediction API..."):
                payload = {"model": model_choice, "data": df.to_dict(orient="records")}
                response = requests.post(f"{API_URL}/predict", json=payload)

                if response.status_code == 200:
                    pred_df = pd.DataFrame(response.json()["predictions"])
                    st.success("✅ Predictions generated!")
                    st.subheader("📈 Model Predictions")
                    st.dataframe(pred_df)
                else:
                    st.error(f"❌ API Error: {response.status_code} - {response.json().get('detail')}")
        except Exception as e:
            st.error(f"⚠️ Request failed: {e}")
else:
    st.info("👈 Please upload a CSV file to begin.")
