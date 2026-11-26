from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    user_name: str
    password: str
    user_type: str

class UserLogin(BaseModel):
    user_name: str
    password: str

class RefreshToken(BaseModel):
    refresh_token: str

class Organizer(BaseModel):
    user_name: str
    password: str

class Player(BaseModel):
    name: str
    role: str
    team: str
    base_points: int = 0

class Match(BaseModel):
    match_name: str
    team_1: str
    team_2: str
    venue: str
    match_time: datetime
    deadline: datetime

class Tournament(BaseModel):
    tournament_name: str
    season: str
    matches: list[Match] = []

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
