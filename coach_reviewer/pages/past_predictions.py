import traceback
from datetime import datetime, timedelta
from io import StringIO

import streamlit as st
import pandas as pd
import requests

END_POINT = "past-predictions"

st.set_page_config(page_title="Past Predictions", page_icon="📒")

# Sidebar date filters
st.sidebar.markdown('### Select date range for predictions:')
tomorrow = datetime.now() + timedelta(days=1)
start_date = st.sidebar.date_input('From', datetime(2025, 3, 1))
end_date = st.sidebar.date_input('To', tomorrow)

# API URL resolution
try:
    base_url = st.session_state['base_url']
    url = f"{base_url}/{END_POINT}"
except KeyError:
    url = 'http://localhost:8000/past-predictions'
    st.warning('Defaulting to localhost. Please visit the homepage to configure the session.')

# Request and filtering
try:
    response = requests.get(url)
    if response.status_code == 200:
        df = pd.read_json(StringIO(response.text), orient='records')

        # Ensure timestamp is datetime
        df['insertion_timestamp'] = pd.to_datetime(df['insertion_timestamp'])

        # Filter by date
        filtered_df = df[
            (df['insertion_timestamp'] >= pd.to_datetime(start_date)) &
            (df['insertion_timestamp'] <= pd.to_datetime(end_date))
        ].reset_index(drop=True)

        st.success(f"✅ Showing {len(filtered_df)} predictions between {start_date} and {end_date}")
        st.dataframe(filtered_df)

        # Optional CSV download
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", data=csv, file_name="past_predictions.csv", mime="text/csv")

    else:
        st.error(f"❌ Request failed: {response.status_code}")
except Exception as e:
    st.warning("⚠️ Server error or API not reachable.")
    st.error(traceback.format_exc())
