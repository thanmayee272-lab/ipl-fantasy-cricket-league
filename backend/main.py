<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< HEAD

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
=======
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
import functions 
=======

from fastapi import FastAPI, HTTPException, Header
import functions
from model import (User, UserLogin,Organizer, Player, RefreshToken, Tournament, FantasyTeamPlayer)
>>>>>>> Stashed changes
=======

from fastapi import FastAPI, HTTPException, Header
import functions
from model import (User, UserLogin,Organizer, Player, RefreshToken, Tournament, FantasyTeamPlayer)
>>>>>>> Stashed changes

app = FastAPI()

class Users(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    user_name: str = Field(min_length=1)
    password: str = Field(min_length=1)

class OrganizerRegister(BaseModel):
    user_name: str = Field(min_length=3)
    password: str = Field(min_length=6)
    

@app.get("/")
def hello():
    return {"message": "Welcome to IPL Fantasy Cricket League"}


# CHECK USER ROLE
def check_role(token, allowed_roles):

    payload = functions.verify_token(token=token,token_type="access" )
    if not payload:
        raise HTTPException( status_code=401, detail="Invalid or expired token" )
    username = payload.get("username")
    user_type = functions.get_user_type(username)
    if not user_type:
        raise HTTPException( status_code=401, detail="User not found" )
    if user_type not in allowed_roles:
        raise HTTPException( status_code=403,  detail="Permission denied" )
    return username

# A1 - REGISTER USER
@app.post("/auth/register", status_code=201)
def register(user: User):
    response = functions.register_user( user_name=user.username,  password=user.password, user_type="user")
    if response:
        return {"message": "User registered successfully"}
    raise HTTPException( status_code=400, detail="User already exists")



# A2 - LOGIN
@app.post("/auth/login")
def login(user: UserLogin):
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    token = functions.verify_login(username=user.user_name, password=user.password)
=======

    token = functions.verify_login( username=user.user_name,  password=user.password )

>>>>>>> Stashed changes
=======

    token = functions.verify_login( username=user.user_name,  password=user.password )

>>>>>>> Stashed changes
    if not token:
        raise HTTPException( status_code=401, detail="Invalid username or password")
    return token


<<<<<<< Updated upstream
<<<<<<< Updated upstream
# E1
@app.post("/admin/organizers")
def create_organizer(user: OrganizerRegister, token=Header(None)):
    check_role(token, ["admin"])
    if functions.create_organizer(user_name=user.user_name, password=user.password):
        return {"message": "Organizer created successfully"}
    raise HTTPException(status_code=409, detail="User already exists")
>>>>>>> b19fcbec8da798ea6603387c2c5c0fd50de24846
=======
=======
>>>>>>> Stashed changes
# A3 - REFRESH TOKEN
@app.post("/auth/refresh")
def refresh(data: RefreshToken):

    response = functions.refresh_access_token( refresh_token=data.refresh_token )
    if not response:
        raise HTTPException( status_code=401, detail="Invalid or expired refresh token" )
    return response


# E1 - CREATE ORGANIZER
@app.post("/admin/organizers")
def create_organizer( user: Organizer, token: str = Header(...)):

    check_role(token, ["admin"])
    response = functions.create_organizer( user_name=user.username, password=user.password)
    if response:
        return {"message": "Organizer created successfully"}

    raise HTTPException( status_code=409, detail="User already exists")


# E2 - ADD CRICKET PLAYER
@app.post("/players")
def add_player(data: Player,token: str = Header(...)):
    check_role(token, ["organizer"])
    if data.role.lower() not in functions.PLAYER_ROLES:
        raise HTTPException( status_code=400,detail="Invalid player role")

    response = functions.add_player(name=data.player_name, role=data.role.lower(),team=data.team, base_points=data.base_points )
    if not response:
        raise HTTPException( status_code=400,  detail="Unable to add player"  )
    return response


# E3 - GET ALL PLAYERS
@app.get("/players")
def get_players(role: str = None,team: str = None,token: str = Header(...)):

    check_role( token,  ["user", "organizer", "admin"] )
    if role is not None and role.lower() not in functions.PLAYER_ROLES:
        raise HTTPException( status_code=422,  detail="Invalid player role")

    return functions.get_all_players(
        role.lower() if role else None,
        team
    )


<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
