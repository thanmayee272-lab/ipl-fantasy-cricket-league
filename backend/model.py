from pydantic import BaseModel, Field

class User(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    user_name: str = Field(min_length=1)
    password: str = Field(min_length=1)

class RefreshToken(BaseModel):
    refresh_token: str

class Organizer(BaseModel):
    username: str
    password: str

class Player(BaseModel):
    player_name: str
    role: str
    team: str
    base_points: float

class Tournament(BaseModel):
    tournament_name: str
    season: str

class FantasyTeamPlayer(BaseModel):
    fantasy_team_id: int
    player_id: int