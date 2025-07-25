import streamlit as st
import requests
import json

st.set_page_config(page_title="Individual Prediction", page_icon="⚽")
st.title("📊 Predict Football Player Overall")

# 🔗 API Endpoint
url = st.session_state.get("base_url", "http://localhost:8000") + "/predict"

# 🎛 Feature Schema
NUMERIC_COLS = [
    "age", "height_cm", "weight_kg", "pace", "shooting", "passing", "dribbling", "defending", "physic",
    "attacking_crossing", "attacking_finishing", "attacking_heading_accuracy",
    "attacking_short_passing", "attacking_volleys", "skill_dribbling", "skill_curve", "skill_fk_accuracy",
    "skill_long_passing", "skill_ball_control", "movement_acceleration", "movement_sprint_speed",
    "movement_agility", "movement_reactions", "movement_balance", "power_shot_power", "power_jumping",
    "power_stamina", "power_strength", "power_long_shots", "mentality_aggression",
    "mentality_interceptions", "mentality_positioning", "mentality_vision", "mentality_penalties",
    "mentality_composure", "defending_standing_tackle", "defending_sliding_tackle", "potential"
]

CATEGORICAL_COLS = {
    "preferred_foot": ["Left", "Right"],
    "main_position": ["CB", "LB", "RB", "CDM", "CM", "CAM", "LW", "RW", "ST"],
    "att_work_rate": ["Low", "Medium", "High"],
    "def_work_rate": ["Low", "Medium", "High"],
    "nationality_grouped": ["France", "Brazil", "Spain", "Germany", "Argentina", "Portugal", "Netherlands", "Other"]
}

# 🧮 Form Input
with st.form("individual_form"):
    st.subheader("⚙️ Enter Player Features")

    numeric_inputs = {col: st.number_input(f"{col.replace('_', ' ').title()}", value=50.0) for col in NUMERIC_COLS}
    categorical_inputs = {col: st.selectbox(f"{col.replace('_', ' ').title()}", options)
                          for col, options in CATEGORICAL_COLS.items()}

    submit_btn = st.form_submit_button("📨 Submit for Prediction")

# 🚀 API Call on Form Submit
if submit_btn:
    player_features = {**numeric_inputs, **categorical_inputs}
    try:
        response = requests.post(url, json={"features": [player_features]})
        if response.status_code == 200:
            result = response.json()

            if isinstance(result, list) and len(result) > 0 and "predicted_overall" in result[0]:
                st.success("🎯 Prediction Successful")
                st.metric("Predicted Overall", round(result[0]["predicted_overall"], 2))
            elif isinstance(result, dict) and "predicted_overall" in result:
                st.success("🎯 Prediction Successful")
                st.metric("Predicted Overall", round(result["predicted_overall"], 2))
            else:
                st.warning("✅ Unexpected response format:")
                st.write(result)
        else:
            st.error(f"❌ API returned status: {response.status_code}")
    except Exception as e:
        st.error(f"⚠️ Request failed: {e}")

# 🧾 Paste JSON Option
st.divider()
st.subheader("📥 Paste Raw JSON for Prediction")
raw_json = st.text_area("Paste JSON with 'features' key below:", height=250)

if st.button("📨 Predict from Pasted JSON"):
    try:
        parsed = json.loads(raw_json)
        if not isinstance(parsed, dict) or "features" not in parsed:
            raise ValueError("Invalid format — must be a JSON object with 'features' list")
        if not isinstance(parsed["features"], list) or len(parsed["features"]) == 0:
            raise ValueError("'features' must be a non-empty list of dicts")
        if not isinstance(parsed["features"][0], dict):
            raise ValueError("Each feature must be a dict")

        response = requests.post(url, json=parsed)
        if response.status_code == 200:
            result = response.json()

            if isinstance(result, list) and len(result) > 0 and "predicted_overall" in result[0]:
                prediction_value = result[0]["predicted_overall"]
            elif isinstance(result, dict) and "predicted_overall" in result:
                prediction_value = result["predicted_overall"]
            else:
                st.warning("✅ Unexpected response format:")
                st.write(result)
                prediction_value = None

            if prediction_value is not None:
                st.success("🎯 Predicted Overall")
                st.metric("Overall", round(prediction_value, 2))
        else:
            st.error(f"❌ API Error: {response.status_code}")
    except Exception as e:
        st.error(f"❌ JSON parsing or request failed: {e}")