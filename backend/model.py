from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
import functions 

class Users(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    user_name: str = Field(min_length=1)
    password: str = Field(min_length=1)

class OrganizerRegister(BaseModel):
    user_name: str = Field(min_length=3)
    password: str = Field(min_length=6)
    

class RefreshTokenRequest(BaseModel):
    refresh_token: str
    
class PlayerDetails(BaseModel):
    name: str
    role: str
    team: str
    base_points: int