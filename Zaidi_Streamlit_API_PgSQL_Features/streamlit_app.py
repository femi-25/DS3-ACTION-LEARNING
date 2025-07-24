import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="MVP Talent Detection App", layout="centered")
st.title("🏆 Welcome to MVP Talent Detection App")

# If already logged in
if "token" in st.session_state:
    st.success(f"✅ Logged in as **{st.session_state['username']}**")
    if st.button("Logout"):
        st.session_state.clear()
        st.experimental_rerun()

else:
    st.subheader("🔐 Login or Register")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if not username or not password:
                st.warning("⚠️ Please enter both username and password.")
            else:
                try:
                    response = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state["token"] = data["access_token"]
                        st.session_state["username"] = username
                        st.session_state["role"] = "user"  # Placeholder — later fetch from /me
                        st.success("✅ Login successful!")
                        st.experimental_rerun()
                    else:
                        st.error(f"❌ {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"❌ Login failed: {e}")

    with tab2:
        reg_username = st.text_input("New Username")
        reg_email = st.text_input("Email")
        reg_fullname = st.text_input("Full Name")
        reg_password = st.text_input("Password", type="password")

        if st.button("Register"):
            if not all([reg_username, reg_email, reg_fullname, reg_password]):
                st.warning("⚠️ Please fill in all fields.")
            else:
                try:
                    response = requests.post(
                        f"{API_URL}/register",
                        json={
                            "username": reg_username,
                            "email": reg_email,
                            "full_name": reg_fullname,
                            "password": reg_password,
                        }
                    )
                    if response.status_code == 200:
                        st.success("✅ Registered successfully! Now login.")
                    else:
                        st.error(f"❌ {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"❌ Registration failed: {e}")
