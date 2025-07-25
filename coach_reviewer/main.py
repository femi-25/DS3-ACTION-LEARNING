import streamlit as st

st.set_page_config(
    page_title='coach_reviewer',
    page_icon='⚽',
)

st.write("# Welcome to the coach_reviewer! ⚽")

st.sidebar.success("Select a module from the sidebar")

st.markdown(
    """
    This app helps you analyze and compare football players using statistical models and similarity scoring.  
    **👈 Select a module from the sidebar** to:
    - Predict a player's overall rating from individual attributes
    - Find similar players based on age, potential, and overall
    - Retrieve and filter past predictions stored in the database

    ### Data Sources
    - [Football Player Stats Dataset](https://www.kaggle.com/)
    - Custom GNN-based similarity scoring engine
    """
)


# 🔗 Backend URL setup
SERVER_URL = "http://127.0.0.1"
SERVER_PORT = "8000"
BASE_URL = SERVER_URL + ":" + SERVER_PORT


if 'base_url' not in st.session_state:
    st.session_state['base_url'] = BASE_URL