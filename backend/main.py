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

# A1
@app.post("/auth/register")
def register(data: User):
    if data.user_type not in ["admin", "organizer", "user"]:
        raise HTTPException(status_code=400, detail="Invalid user type")
    result = functions.register_user(data.user_name, data.password, data.user_type)
    if not result:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User registered successfully"}

# A2
@app.post("/auth/login")
def login(data: UserLogin):
    result = functions.verify_login(data.user_name, data.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return result

# A3
@app.post("/auth/refresh")
def refresh_token(data: RefreshToken):
    result = functions.refresh_access_token(data.refresh_token)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
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

# E2
@app.post("/players")
def add_player(data: Player, token: str = Header()):
    user_name = get_logged_in_user(token)
    check_role(user_name, "organizer")
    result = functions.add_player(data.name, data.role, data.team, data.base_points)
    if not result:
        raise HTTPException(status_code=400, detail="Invalid player role")
    return result

# E3 
@app.get("/players")
def get_players(role: str = None, team: str = None):
    return functions.get_all_players(role, team)

# E4
@app.get("/players/{player_id}")
def get_player(player_id: int):
    result = functions.get_player_by_id(player_id)
    if not result:
        raise HTTPException(status_code=404, detail="Player not found")
    return result

# E5 
@app.post("/tournaments")
def add_tournament(data: Tournament, token: str = Header()):
    user_name = get_logged_in_user(token)
    check_role(user_name, "organizer")
    match_list = []
    for match in data.matches:
        match_list.append({"match_name": match.match_name, "team_1": match.team_1,"team_2": match.team_2,"venue": match.venue,"match_time": match.match_time, "deadline": match.deadline })
    result = functions.create_tournament( user_name, data.tournament_name, data.season, match_list)
    if not result:
        raise HTTPException(status_code=400, detail="Could not create tournament")
    return result

# E6
@app.get("/tournaments")
def get_tournaments():
    return functions.get_all_tournaments()

# E7 
@app.post("/fantasy-teams")
def add_fantasy_team(data: FantasyTeam, token: str = Header()):
    user_name = get_logged_in_user(token)
    check_role(user_name, "user")
    result = functions.create_fantasy_team(user_name, data.team_name, data.match_id)
    if not result:
        raise HTTPException(status_code=400, detail="Invalid match")
    return result

# E8
@app.post("/fantasy-teams/{fantasy_team_id}/players")
def add_player_to_team(fantasy_team_id: int, data: FantasyTeamPlayer, token: str = Header()):
    user_name = get_logged_in_user(token)
    check_role(user_name, "user")
    result = functions.add_player_to_fantasy_team( user_name,fantasy_team_id, data.player_id)
    if not result:
        raise HTTPException( status_code=400,detail="Could not add player. Check team ownership, deadline, role limit and 11-player limit.")
    return result

# E9
@app.delete("/fantasy-teams/{fantasy_team_id}/players/{player_id}")
def remove_player_from_team(fantasy_team_id: int,player_id: int, token: str = Header()):
    user_name = get_logged_in_user(token)
    check_role(user_name, "user")
    result = functions.remove_player_from_fantasy_team(user_name,fantasy_team_id,player_id)
    if not result:
        raise HTTPException(status_code=400, detail="Could not remove player")
    return result

# E10 
@app.get("/fantasy-teams")
def get_my_teams(token: str = Header()):
    user_name = get_logged_in_user(token)
    check_role(user_name, "user")
    return functions.get_my_fantasy_teams(user_name)

#E11
@app.post("/contests")
def add_contest(data: Contest, token: str = Header()):
    user_name = get_logged_in_user(token)
    check_role(user_name, "organizer")
    result = functions.create_contest(user_name, data.contest_name, data.match_id)
    if not result:
        raise HTTPException(status_code=400, detail="Invalid match")
    return result


# E12 - User joins contest with fantasy team
@app.post("/contests/{contest_id}/join")
def join_contest(contest_id: int, data: JoinContest,token: str = Header()):
    user_name = get_logged_in_user(token)
    check_role(user_name, "user")
    result = functions.join_contest(user_name, contest_id, data.fantasy_team_id)
    if not result:
        raise HTTPException(status_code=400,detail="Could not join contest. Check team ownership, match and deadline.")
    return result

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

#E14
@app.get("/contests/{contest_id}/leaderboard")
def get_leaderboard(contest_id: int):
    result = functions.get_contest_leaderboard(contest_id)
    if result is False:
        raise HTTPException(status_code=404, detail="Contest not found")
    return result


# E15 - User views own fantasy points history
@app.get("/users/me/points-history")
def get_my_points_history(token: str = Header()):
    user_name = get_logged_in_user(token)
    check_role(user_name, "user")
    return functions.get_points_history(user_name)