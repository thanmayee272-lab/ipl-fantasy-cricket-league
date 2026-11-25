from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta
import functions 

class User(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    user_name: str = Field(min_length=1)
    password: str = Field(min_length=1)

class RefreshToken:
    refresh_token: str  

class Organizer(BaseModel):
    username: str
    password: str

class Player(BaseModel):
    player_name: str
    role: str
    team: str
    base_points: float

class Match(BaseModel):
    team_1: str
    team_2: str
    venue: str
    match_time: datetime

class Tournament(BaseModel):
    tournament_name: str
    season: str
    matches: list[Match] = Field(default=list)

class FantasyTeam(BaseModel):
    team_name: str
    match_id: int

class FantasyTeamPlayer(BaseModel):
    player_id: int

class Contest(BaseModel):
    contest_name: str
    match_id: int

class JoinContest(BaseModel):
    fantasy_team_id: int

class PlayerPerformance(BaseModel):
    player_id: int
    runs: int = 0
    fours: int = 0
    sixes: int = 0
    wickets: int = 0
    catches: int = 0
    run_outs: int = 0
    stumpings: int = 0

class MatchPerformance(BaseModel):
    performances: list[PlayerPerformance]