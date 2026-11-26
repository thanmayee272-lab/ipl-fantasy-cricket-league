from fastapi import FastAPI, HTTPException, Header
import functions
from model import (User, UserLogin, RefreshToken, Organizer, Player, Tournament, FantasyTeam, FantasyTeamPlayer, Contest, JoinContest,MatchPerformance,)
app = FastAPI()

def get_logged_in_user(token):
    user_name = functions.verify_token(token, "access")
    if not user_name:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user_name

def check_role(user_name, required_role):
    user_type = functions.get_user_type(user_name)
    if user_type != required_role:
        raise HTTPException(status_code=403, detail="You do not have permission")

# A2
@app.post("/auth/login")
def login(data: UserLogin):
    result = functions.verify_login(data.user_name, data.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return result

# E1 
@app.post("/organizers")
def add_organizer(data: Organizer, token: str = Header()):
    user_name = get_logged_in_user(token)
    check_role(user_name, "admin")
    result = functions.create_organizer(data.user_name, data.password)
    if not result:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "Organizer created successfully"}

# E4
@app.get("/players/{player_id}")
def get_player(player_id: int):
    result = functions.get_player_by_id(player_id)
    if not result:
        raise HTTPException(status_code=404, detail="Player not found")
    return result

# E7 
@app.post("/fantasy-teams")
def add_fantasy_team(data: FantasyTeam, token: str = Header()):
    user_name = get_logged_in_user(token)
    check_role(user_name, "user")
    result = functions.create_fantasy_team(user_name, data.team_name, data.match_id)
    if not result:
        raise HTTPException(status_code=400, detail="Invalid match")
    return result

# E10 
@app.get("/fantasy-teams")
def get_my_teams(token: str = Header()):
    user_name = get_logged_in_user(token)
    check_role(user_name, "user")
    return functions.get_my_fantasy_teams(user_name)

# E13 
@app.post("/matches/{match_id}/performances")
def add_performances( match_id: int,data: MatchPerformance, token: str = Header()):
    user_name = get_logged_in_user(token)
    check_role(user_name, "organizer")
    performance_list = []
    for performance in data.performances:
        performance_list.append({"player_id": performance.player_id,"runs": performance.runs,"fours": performance.fours,
        "sixes": performance.sixes, "wickets": performance.wickets,"catches": performance.catches, "run_outs": performance.run_outs,"stumpings": performance.stumpings})
    result = functions.publish_performances(match_id, performance_list)
    if not result:
        raise HTTPException( status_code=400, detail="Could not publish performances. Check match, players and duplicate records." )
    return result
