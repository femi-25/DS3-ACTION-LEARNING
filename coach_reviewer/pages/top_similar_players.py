import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Top Similar Players", page_icon="🎯")
st.title("🔁 Find Similar Players by Stats")

# Load base URL
try:
    base_url = st.session_state.get("base_url", "http://localhost:8000")
    url = base_url + "/similar_players"
except Exception:
    base_url = "http://localhost:8000"
    url = base_url + "/similar_players"
    st.warning("Session state missing — defaulting to localhost")

# Fetch previously predicted players to select as reference
@st.cache_data
def fetch_players():
    try:
        response = requests.get(f"{base_url}/past-predictions")
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []

players = fetch_players()
player_id_to_label = {
    p["id"]: f'Player {p["id"]} | {p["features"].get("main_position", "")} | Overall: {p.get("predicted_overall", "")}'
    for p in players
}

if not player_id_to_label:
    st.warning("No past predictions found. Please predict a player first.")
else:
    with st.form("similar_form"):
        reference_id = st.selectbox(
            "Select a Reference Player",
            options=list(player_id_to_label.keys()),
            format_func=lambda x: player_id_to_label[x]
        )
        top_n = st.slider("Number of Similar Players", 1, 20, 5)
        submit = st.form_submit_button("🔍 Find Similar")

    if submit:
        params = {"reference_player_id": reference_id, "top_n": top_n}

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                similar_players = response.json()

                if not similar_players:
                    st.info("📭 No similar players found.")
                else:
                    df = pd.DataFrame(similar_players)
                    df = df.rename(columns={
                        "player_id": "Player ID",
                        "main_position": "Position",
                        "nationality": "Nationality",
                        "overall": "Predicted Overall",
                        "similarity_score": "Similarity Score"
                    })
                    df = df.sort_values(by="Similarity Score", ascending=False).reset_index(drop=True)

                    st.success(f"✅ Top {top_n} similar players to Player {reference_id}")
                    st.dataframe(df)

                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("📥 Download CSV", data=csv, file_name="similar_players.csv", mime="text/csv")
            else:
                st.error(f"❌ API Error: {response.status_code}")
        except Exception as e:
            st.error(f"⚠️ Request failed: {e}")
