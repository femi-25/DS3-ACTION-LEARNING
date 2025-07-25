from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import create_user, get_user_by_username
from auth_utils import check_password, create_access_token

app = FastAPI()

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@app.post("/register")
def register(user_data: UserCreate):
    try:
        user = create_user(user_data)
        return {
            "status": "success",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "created_at": user["created_at"].isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
def login(user_data: UserLogin):
    user = get_user_by_username(user_data.username)
    if not user or not check_password(user_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": user["username"]})
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.get("/predictions_with_sensitive_features")
def get_predictions_with_sensitive_features():
    # TODO: Replace this with real DB query later
    return [
        {"y_true": 1, "y_pred_baseline": 0, "y_pred_fair": 1, "gender": "F"},
        {"y_true": 0, "y_pred_baseline": 0, "y_pred_fair": 0, "gender": "M"},
        {"y_true": 1, "y_pred_baseline": 1, "y_pred_fair": 1, "gender": "F"},
        {"y_true": 1, "y_pred_baseline": 0, "y_pred_fair": 1, "gender": "M"},
        {"y_true": 0, "y_pred_baseline": 1, "y_pred_fair": 0, "gender": "F"}
    ]

@app.get("/shap_explanations")
def get_shap_explanations():
    return {
        "feature_names": ["Age", "Height", "Weight", "Sport_encoded", "Team_encoded"],
        "global_shap_values": [0.15, 0.25, 0.35, 0.1, 0.05],
        "local_explanations": [
            {"Age": 0.2, "Height": 0.1, "Weight": 0.05, "Sport_encoded": 0.4, "Team_encoded": 0.25},
            {"Age": 0.1, "Height": 0.15, "Weight": 0.3, "Sport_encoded": 0.2, "Team_encoded": 0.25}
        ]
    }

from fastapi import Query

# Dummy player dataset for illustration
players_db = {
    "1": {"id": "1", "name": "Alice", "age": 25, "sport": "Soccer", "team": "A"},
    "2": {"id": "2", "name": "Bob", "age": 26, "sport": "Soccer", "team": "A"},
    "3": {"id": "3", "name": "Charlie", "age": 24, "sport": "Basketball", "team": "B"},
    # Add more players or load real dataset
}

@app.get("/player_similarity")
def player_similarity(player_id: str = Query(..., description="Player ID to find similarities for")):
    if player_id not in players_db:
        raise HTTPException(status_code=404, detail="Player not found")

    # Dummy similarity logic: return players from the same sport and different id
    player = players_db[player_id]
    similar_players = [
        p for pid, p in players_db.items() 
        if pid != player_id and p["sport"] == player["sport"]
    ]

    return {"player_id": player_id, "similar_players": similar_players}

@app.get("/fairness_metrics")
def fairness_metrics():
    # Replace with real fairness computation or DB query
    return {
        "demographic_parity_difference": 0.05,
        "equal_opportunity_difference": 0.03,
        "statistical_parity_difference": 0.04,
        "disparate_impact": 0.85
    }

from typing import List, Dict
from fastapi import Request
from pydantic import BaseModel

class PredictionRequest(BaseModel):
    model: str
    data: List[Dict]  # List of athlete records

from model_runner import predict_from_model

@app.post("/predict")
async def predict(payload: PredictionRequest):
    predictions = predict_from_model(payload.data, payload.model)

    if any("error" in p for p in predictions):
        raise HTTPException(status_code=400, detail=predictions[0]["error"])

    return {"predictions": predictions}
