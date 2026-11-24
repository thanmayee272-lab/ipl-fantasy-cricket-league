
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import function

app = FastAPI(
    title="IPL Fantasy Cricket League API",
    description="IPL Fantasy Cricket League Backend API",
    version="1.0.0"
)

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@app.post("/auth/refresh")
def refresh(data: RefreshTokenRequest):

    response = function.refresh_access_token(refresh_token=data.refresh_token)
    if not response:
        raise HTTPException( status_code=401, detail="Invalid or expired refresh token")

    return response
