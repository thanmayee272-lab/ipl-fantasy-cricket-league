from fastapi import FastAPI, HTTPException, Header
import functions 
from model import Users, Organizer, Player, RefreshToken, Match, Tournament, FantasyTeam, FantasyTeamPlayer, Contest, JoinContest, PlayerPerformance, MatchPerformance

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Welcome to IPL Fantasy Cricket League"}
    
# A1
@app.post("/auth/register", status_code=201)
def register(user: Users):
    if user.username.strip() == "" or user.password.strip() == "":
        raise HTTPException(status_code=422, detail="Username and password are required")
    response = functions.register_user(user_name=user.username, password=user.password, user_type="user")
    if response:
        return {"message": "User registered successfully"}
    raise HTTPException(status_code=400, detail="User already exists")


# A2
@app.post("/auth/login")
def login(user: Users):
    token = functions.verify_login(username=user.user_name, password=user.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return token

def check_role(token, allowed_roles):
    username = functions.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_type = functions.get_user_type(username)
    if user_type not in allowed_roles:
        raise HTTPException(status_code=403, detail="Permission denied")

@app.post("/auth/refresh")
def refresh(data: RefreshToken):
    response = function.refresh_access_token( refresh_token=data.refresh_token)
    if not response: raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    return response  

# E1
@app.post("/admin/organizers")
def create_organizer(user: Organizer, token=Header(None)):
    check_role(token, ["admin"])
    if functions.create_organizer(user_name=user.user_name, password=user.password):
        return {"message": "Organizer created successfully"}
    raise HTTPException(status_code=409, detail="User already exists")


@app.post("/players")
def add_player(data: Player, token: str = Header(...)):
    payload = function.verify_token(token, "access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload["role"].lower() != "organizer":
        raise HTTPException(status_code=403, detail="Only organizers can add players")
    if data.role.lower() not in ["batsman", "bowler", "all-rounder", "wicketkeeper"]:
        raise HTTPException(status_code=400, detail="Invalid player role")
    response = function.add_player( name=data.name, role=data.role,team=data.team,base_points=data.base_points )
    return response