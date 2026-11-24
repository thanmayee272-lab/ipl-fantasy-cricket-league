from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import function

app = FastAPI(
    title="Expense Tracker API",
    description="API with JWT Authentication and Refresh Token",
    version="1.0.0"
)

# Pydantic Model - Refresh Token
class RefreshTokenRequest(BaseModel):
    refresh_token: str


# E9 - Refresh Token Endpoint
@app.post("/refresh")
def refresh(data: RefreshTokenRequest):

    # Generate a new access token using the refresh token
    response = function.refresh_access_token(
        refresh_token=data.refresh_token
    )

    # Check whether the refresh token is valid
    if not response:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token"
        )

    return response