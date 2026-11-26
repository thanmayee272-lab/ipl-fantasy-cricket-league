from datetime import datetime, timezone, timedelta
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import Integer, String, Column, create_engine, DateTime, ForeignKey
from sqlalchemy.orm import Session, declarative_base

DB_PATH = "fantasy.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_name = Column(String, unique=True)
    password = Column(String)
    user_type = Column(String)

class Players(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)
    team = Column(String)
    base_points = Column(Integer, default=0)

class Tournaments(Base):
    __tablename__ = "tournaments"
    id = Column(Integer, primary_key=True)
    tournament_name = Column(String)
    season = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"))

class Matches(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
    match_name = Column(String)
    team_1 = Column(String)
    team_2 = Column(String)
    venue = Column(String)
    match_time = Column(DateTime)
    deadline = Column(DateTime)
    status = Column(String, default="upcoming")
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))

class FantasyTeams(Base):
    __tablename__ = "fantasy_teams"
    id = Column(Integer, primary_key=True)
    team_name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    match_id = Column(Integer, ForeignKey("matches.id"))

class FantasyTeamPlayers(Base):
    __tablename__ = "fantasy_team_players"
    id = Column(Integer, primary_key=True)
    fantasy_team_id = Column(Integer, ForeignKey("fantasy_teams.id"))
    player_id = Column(Integer, ForeignKey("players.id"))

class Contests(Base):
    __tablename__ = "contests"
    id = Column(Integer, primary_key=True)
    contest_name = Column(String)
    match_id = Column(Integer, ForeignKey("matches.id"))
    created_by = Column(Integer, ForeignKey("users.id"))

class ContestEntries(Base):
    __tablename__ = "contest_entries"
    id = Column(Integer, primary_key=True)
    contest_id = Column(Integer, ForeignKey("contests.id"))
    fantasy_team_id = Column(Integer, ForeignKey("fantasy_teams.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

class PlayerPerformances(Base):
    __tablename__ = "player_performances"
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    player_id = Column(Integer, ForeignKey("players.id"))
    runs = Column(Integer, default=0)
    fours = Column(Integer, default=0)
    sixes = Column(Integer, default=0)
    wickets = Column(Integer, default=0)
    catches = Column(Integer, default=0)
    run_outs = Column(Integer, default=0)
    stumpings = Column(Integer, default=0)
    fantasy_points = Column(Integer, default=0)

Base.metadata.create_all(engine)
ACCESS_TOKEN_EXPIRY = 15
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60
SECRET_KEY = "ipl_fantasy_secret_key_change_before_deployment_2026"
ALGORITHM = "HS256"

ph = PasswordHasher()

# A1
def register_user(user_name, password, user_type):
    session = Session(engine)
    user_exists = session.query(Users).filter_by(user_name=user_name).first()
    if user_exists:
        session.close()
        return False
    user = Users(user_name=user_name, password=ph.hash(password), user_type=user_type)
    session.add(user)
    session.commit()
    session.close()
    return True

# A2
def verify_login(user_name, password):
    session = Session(engine)
    user = session.query(Users).filter_by(user_name=user_name).first()
    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.password, password)
    except (VerifyMismatchError):
        session.close()
        return False
    user_type = user.user_type
    session.close()
    access_token = create_token(user_name, "access", user_type)
    refresh_token = create_token(user_name, "refresh", user_type)
    return {"access_token": access_token, "refresh_token": refresh_token}

# Creating access and refresh tokens
def create_token(user_name, token_type, user_type="user"):
    time = ACCESS_TOKEN_EXPIRY
    if token_type == "refresh":
        time = REFRESH_TOKEN_EXPIRY
    payload = {"user_name": user_name, "token_type": token_type, "user_type": user_type, "exp": datetime.now(timezone.utc) + timedelta(minutes=time)}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Verifying access or refresh token
def verify_token(token, token_type):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return False
    if payload.get("token_type") != token_type:
        return False
    return payload.get("user_name")

# Getting the user's role
def get_user_type(user_name):
    session = Session(engine)
    user = session.query(Users).filter_by(user_name=user_name).first()
    if user is None:
        session.close()
        return False
    user_type = user.user_type
    session.close()
    return user_type

# A3
def refresh_access_token(refresh_token):
    user_name = verify_token(refresh_token, "refresh")
    if not user_name:
        return False
    session = Session(engine)
    user = session.query(Users).filter_by(user_name=user_name).first()
    if user is None:
        session.close()
        return False
    access_token = create_token(user.user_name, "access", user.user_type)
    session.close()
    return {"access_token": access_token}

# E1
def create_organizer(user_name, password):
    session = Session(engine)
    existing_user = session.query(Users).filter_by(user_name=user_name).first()
    if existing_user is not None:
        session.close()
        return False
    user = Users(user_name=user_name, password=ph.hash(password), user_type="organizer")
    session.add(user)
    session.commit()
    session.close()
    return True

# E2
def add_player(name, role, team, base_points):
    allowed_roles = ["batsman", "bowler", "all-rounder", "wicketkeeper"]
    if role.lower() not in allowed_roles:
        return False
    session = Session(engine)
    player = Players(name=name, role=role, team=team, base_points=base_points)
    session.add(player)
    session.commit()
    player_id = player.id
    session.close()
    return {"message": "Player added successfully",
        "player_id": player_id, "name": name,"role": role, "team": team, "base_points": base_points}

# E3
def get_all_players(role=None, team=None):
    session = Session(engine)
    players = session.query(Players)
    if role:
        players = players.filter(Players.role == role.lower())
    if team:
        players = players.filter(Players.team == team)
    response = []
    for player in players.all():
        response.append({"id": player.id, "name": player.name, "role": player.role,"team": player.team, "base_points": player.base_points})
    session.close()
    return response

# E4
def get_player_by_id(player_id):
    session = Session(engine)
    player = session.query(Players).filter_by(id=player_id).first()
    if player is None:
        session.close()
        return False
    response = {"id": player.id, "name": player.name, "role": player.role, "team": player.team, "base_points": player.base_points}
    session.close()
    return response

# E5
def create_tournament(user_name, tournament_name, season, matches):
    session = Session(engine)
    user = session.query(Users).filter_by(user_name=user_name).first()
    if user is None:
        session.close()
        return False
    tournament = Tournaments(tournament_name=tournament_name, season=season, created_by=user.id)
    session.add(tournament)
    session.commit()
    tournament_id = tournament.id
    match_list = []
    for match in matches:
        new_match = Matches(
            match_name=match["match_name"],
            team_1=match["team_1"],
            team_2=match["team_2"],
            venue=match["venue"],
            match_time=match["match_time"],
            deadline=match["deadline"],
            tournament_id=tournament_id,
            status="upcoming")
        session.add(new_match)
        session.commit()
        match_list.append({
            "id": new_match.id,
            "match_name": new_match.match_name,
            "team_1": new_match.team_1,
            "team_2": new_match.team_2,
            "venue": new_match.venue,
            "match_time": new_match.match_time,
            "deadline": new_match.deadline,
            "status": new_match.status})
    session.close()
    return {"message": "Tournament created successfully", "tournament_id": tournament_id, "tournament_name": tournament_name,
        "season": season,
        "matches": match_list}

# E6
def get_all_tournaments():
    session = Session(engine)
    tournaments = session.query(Tournaments).all()
    response = []
    for tournament in tournaments:
        matches = session.query(Matches).filter_by(tournament_id=tournament.id).all()
        match_list = []
        for match in matches:
            match_list.append({
                "id": match.id,
                "match_name": match.match_name,
                "team_1": match.team_1,
                "team_2": match.team_2,
                "venue": match.venue,
                "match_time": match.match_time,
                "deadline": match.deadline,
                "status": match.status}) 
        response.append({"id": tournament.id,"tournament_name": tournament.tournament_name,"season": tournament.season,"matches": match_list})
    session.close()
    return response

# E7
def create_fantasy_team(user_name, team_name, match_id):
    session = Session(engine)
    user = session.query(Users).filter_by(user_name=user_name).first()
    match = session.query(Matches).filter_by(id=match_id).first()
    if user is None or match is None:
        session.close()
        return False
    team = FantasyTeams(team_name=team_name,user_id=user.id, match_id=match_id)
    session.add(team)
    session.commit()
    team_id = team.id
    session.close()
    return {"message": "Fantasy team created successfully", "fantasy_team_id": team_id, "team_name": team_name, "match_id": match_id}

#E8
def add_player_to_fantasy_team(user_name, fantasy_team_id, player_id):
    session = Session(engine)
    user = session.query(Users).filter_by(user_name=user_name).first()
    fantasy_team = session.query(FantasyTeams).filter_by(id=fantasy_team_id).first()
    player = session.query(Players).filter_by(id=player_id).first()

    if user is None or fantasy_team is None or player is None:
        session.close()
        return False

    if fantasy_team.user_id != user.id:
        session.close()
        return False

    match = session.query(Matches).filter_by(id=fantasy_team.match_id).first()
    if match is None:
        session.close()
        return False
    deadline = match.deadline
    if deadline is not None:
        if datetime.now() > deadline:
            session.close()
            return False
    existing_player = session.query(FantasyTeamPlayers).filter_by(fantasy_team_id=fantasy_team_id, player_id=player_id).first()
    if existing_player is not None:
        session.close()
        return False
    team_players = session.query(FantasyTeamPlayers).filter_by( fantasy_team_id=fantasy_team_id).all()
    if len(team_players) >= 11:
        session.close()
        return False
    role_limits = { "batsman": 5, "bowler": 5,"all-rounder": 3, "wicketkeeper": 1}
    role_count = 0
    for team_player in team_players:
        old_player = session.query(Players).filter_by(id=team_player.player_id).first()
        if old_player and old_player.role == player.role:
            role_count += 1
    if role_count >= role_limits[player.role]:
        session.close()
        return False
    new_player = FantasyTeamPlayers(fantasy_team_id=fantasy_team_id, player_id=player_id)

    session.add(new_player)
    session.commit()
    session.close()
    return {"message": "Player added to fantasy team successfully"}

# E9
def remove_player_from_fantasy_team(user_name, fantasy_team_id, player_id):
    session = Session(engine)
    user = session.query(Users).filter_by(user_name=user_name).first()
    fantasy_team = session.query(FantasyTeams).filter_by(id=fantasy_team_id).first()
    if user is None or fantasy_team is None:
        session.close()
        return False
    if fantasy_team.user_id != user.id:
        session.close()
        return False
    match = session.query(Matches).filter_by(id=fantasy_team.match_id).first()
    if match is None:
        session.close()
        return False
    deadline = match.deadline
    if deadline is not None:
        if datetime.now() > deadline:
            session.close()
            return False
    team_player = session.query(FantasyTeamPlayers).filter_by( fantasy_team_id=fantasy_team_id, player_id=player_id ).first()
    if team_player is None:
        session.close()
        return False
    session.delete(team_player)
    session.commit()
    session.close()
    return {"message": "Player removed from fantasy team successfully"}

# E10
def get_my_fantasy_teams(user_name):
    session = Session(engine)
    user = session.query(Users).filter_by(user_name=user_name).first()
    if user is None:
        session.close()
        return []
    teams = session.query(FantasyTeams).filter_by(user_id=user.id).all()
    response = []
    for team in teams:
        team_players = session.query(FantasyTeamPlayers).filter_by(fantasy_team_id=team.id).all()
        players = []
        for team_player in team_players:
            player = session.query(Players).filter_by(id=team_player.player_id).first()
            if player:
                players.append({"id": player.id,"name": player.name,"role": player.role,"team": player.team,"base_points": player.base_points})
        response.append({"fantasy_team_id": team.id,"team_name": team.team_name,"match_id": team.match_id,"players": players})
    session.close()
    return response

# E11
def create_contest(user_name, contest_name, match_id):
    session = Session(engine)
    user = session.query(Users).filter_by(user_name=user_name).first()
    match = session.query(Matches).filter_by(id=match_id).first()
    if user is None or match is None:
        session.close()
        return False
    contest = Contests(contest_name=contest_name, match_id=match_id,created_by=user.id)
    session.add(contest)
    session.commit()
    contest_id = contest.id
    session.close()
    return {"message": "Contest created successfully", "contest_id": contest_id, "contest_name": contest_name, "match_id": match_id}


# E12
def join_contest(user_name, contest_id, fantasy_team_id):
    session = Session(engine)
    user = session.query(Users).filter_by(user_name=user_name).first()
    contest = session.query(Contests).filter_by(id=contest_id).first()
    fantasy_team = session.query(FantasyTeams).filter_by(id=fantasy_team_id).first()
    if user is None or contest is None or fantasy_team is None:
        session.close()
        return False
    if fantasy_team.user_id != user.id:
        session.close()
        return False
    if fantasy_team.match_id != contest.match_id:
        session.close()
        return False
    match = session.query(Matches).filter_by(id=contest.match_id).first()
    if match is None:
        session.close()
        return False
    deadline = match.deadline
    if deadline is not None:
        if datetime.now() > deadline:
            session.close()
            return False
    existing_entry = session.query(ContestEntries).filter_by( contest_id=contest_id,fantasy_team_id=fantasy_team_id).first()
    if existing_entry is not None:
        session.close()
        return False
    entry = ContestEntries(contest_id=contest_id,fantasy_team_id=fantasy_team_id, user_id=user.id)
    session.add(entry)
    session.commit()
    session.close()
    return {"message": "Joined contest successfully"}

