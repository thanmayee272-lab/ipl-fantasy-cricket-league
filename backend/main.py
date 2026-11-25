
from fastapi import FastAPI, HTTPException,Header
from pydantic import BaseModel,Field
import function

app = FastAPI(
    title="IPL Fantasy Cricket League API",
    description="IPL Fantasy Cricket League Backend API",
    version="1.0.0"
)

class RefreshTokenRequest(BaseModel):
    refresh_token: str
    
class PlayerDetails(BaseModel):
    name: str
    role: str
    team: str
    base_points: int

@app.post("/auth/refresh")
def refresh(data: RefreshTokenRequest):

    response = function.refresh_access_token( refresh_token=data.refresh_token)
    if not response: raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    return response

@app.post("/players")
def add_player(data: PlayerDetails, token: str = Header(...)):

    payload = function.verify_token(token, "access")

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload["role"].lower() != "organizer":
        raise HTTPException(status_code=403, detail="Only organizers can add players")

    if data.role.lower() not in ["batsman", "bowler", "all-rounder", "wicketkeeper"]:
        raise HTTPException(status_code=400, detail="Invalid player role")

    response = function.add_player(
        name=data.name,
        role=data.role,
        team=data.team,
        base_points=data.base_points
    )

    return response
