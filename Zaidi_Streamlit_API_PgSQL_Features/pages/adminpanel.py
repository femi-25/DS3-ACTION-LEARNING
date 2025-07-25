import streamlit as st

st.title("🔒 Admin Panel")

if "token" not in st.session_state:
    st.warning("Please login to access admin panel.")
    st.stop()

if st.session_state.get("role") != "admin":
    st.error("⛔ You are not authorized to access this page.")
    st.stop()

st.success("Welcome, Admin! You have full control.")
