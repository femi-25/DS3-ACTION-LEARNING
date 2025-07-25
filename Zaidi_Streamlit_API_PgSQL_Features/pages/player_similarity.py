import streamlit as st
import pandas as pd
import requests

st.title("🔍 Player Similarity Search")
st.markdown("Find similar athletes based on performance and demographic features using the similarity model.")

player_id = st.text_input("Enter Player ID or Name (as available in dataset):")

if st.button("Find Similar Players") and player_id:
    try:
        response = requests.get(f"http://localhost:8000/player_similarity?player_id={player_id}")

        if response.status_code == 200:
            similar_players = response.json().get("similar_players", [])
            if similar_players:
                st.success(f"Found {len(similar_players)} similar players.")
                st.dataframe(pd.DataFrame(similar_players))
            else:
                st.warning("No similar players found.")
        else:
            st.error(f"❌ Error fetching similar players: {response.text}")
    except Exception as e:
        st.error(f"Exception occurred: {e}")
