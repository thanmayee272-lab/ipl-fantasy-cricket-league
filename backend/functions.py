from sqlalchemy import Integer, String, Column, create_engine, Date, DateTime, ForeignKey
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime, timezone, timedelta
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

DB_PATH = "fantasy.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()

ACCESS_TOKEN_EXPIRY = 15
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60
SECRET_KEY = "secret1234"
ALGORITHM = "HS256"

ph = PasswordHasher()

PLAYER_ROLES = ["batsman", "bowler", "all-rounder", "wicketkeeper"]


# USER MODEL
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_name = Column(String, unique=True)
    password = Column(String)
    user_type = Column(String, default="user")


# PLAYER MODEL
class Players(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)
    team = Column(String)
    base_points = Column(Integer)


# MATCH MODEL
class Matches(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    match_name = Column(String)
    match_date = Column(Date)
    deadline = Column(DateTime)
    status = Column(String, default="upcoming")


# FANTASY TEAM MODEL
class FantasyTeams(Base):
    __tablename__ = "fantasy_teams"

    id = Column(Integer, primary_key=True)
    team_name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    match_id = Column(Integer, ForeignKey("matches.id"))


# FANTASY TEAM PLAYERS MODEL
class FantasyTeamPlayers(Base):
    __tablename__ = "fantasy_team_players"

    id = Column(Integer, primary_key=True)
    fantasy_team_id = Column(Integer, ForeignKey("fantasy_teams.id"))
    player_id = Column(Integer, ForeignKey("players.id"))


# PLAYER PERFORMANCE MODEL
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


# TOURNAMENT MODEL
class Tournaments(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True)
    tournament_name = Column(String)
    season = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"))


# CONTEST MODEL
class Contests(Base):
    __tablename__ = "contests"

    id = Column(Integer, primary_key=True)
    contest_name = Column(String)
    match_id = Column(Integer, ForeignKey("matches.id"))
    created_by = Column(Integer, ForeignKey("users.id"))


# CONTEST ENTRY MODEL
class ContestEntries(Base):
    __tablename__ = "contest_entries"

    id = Column(Integer, primary_key=True)
    contest_id = Column(Integer, ForeignKey("contests.id"))
    fantasy_team_id = Column(Integer, ForeignKey("fantasy_teams.id"))
    user_id = Column(Integer, ForeignKey("users.id"))


Base.metadata.create_all(engine)


# A1 - REGISTER USER
def register_user(user_name, password, user_type="user"):
    session = Session(engine)

    user_exists = session.query(Users).filter_by(user_name=user_name
    ).first()

    if user_exists:
        session.close()
        return False

    user = Users( user_name=user_name,password=ph.hash(password), user_type=user_type)
    session.add(user)
    session.commit()
    session.close()
    return True


# A2 - LOGIN
def verify_login(username, password):
    session = Session(engine)
    user = session.query(Users).filter_by( user_name=username
    ).first()

    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.password, password)
    except VerifyMismatchError:
        session.close()
        return False

    user_type = user.user_type
    session.close()
    access_token = create_token(username, "access", user_type)
    refresh_token = create_token(username, "refresh", user_type)
    return { "access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


# CREATE TOKEN
def create_token(username, token_type, user_type="user"):
    time = ACCESS_TOKEN_EXPIRY
    if token_type == "refresh":
        time = REFRESH_TOKEN_EXPIRY
    payload = {"username": username, "token_type": token_type,"user_type": user_type,"exp": datetime.now(timezone.utc) + timedelta(minutes=time) }
    token = jwt.encode( payload=payload,key=SECRET_KEY, algorithm=ALGORITHM)

    return token


# VERIFY TOKEN
def verify_token(token, token_type):
    try:
        payload = jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return False
    if payload.get("token_type") != token_type:
        return False
    return payload


# GET USER TYPE
def get_user_type(username):
    session = Session(engine)

    user = session.query(Users).filter_by( user_name=username
    ).first()

    if user is None:
        session.close()
        return False
    user_type = user.user_type
    session.close()
    return user_type


<<<<<<< Updated upstream
# E1

=======
>>>>>>> Stashed changes
# A3 - REFRESH TOKEN
def refresh_access_token(refresh_token):
    payload = verify_token(refresh_token, "refresh")

    if not payload:
        return False

    username = payload.get("username")
    session = Session(engine)
    user = session.query(Users).filter_by( user_name=username
    ).first()

    if user is None:
        session.close()
        return False
    access_token = create_token( user.user_name, "access", user.user_type )
    session.close()
    return { "access_token": access_token}


# E1 - CREATE ORGANIZER
def create_organizer(user_name, password):
    session = Session(engine)

    existing_user = session.query(Users).filter_by(user_name=user_name
    ).first()

    if existing_user:
        session.close()
        return False

    user = Users( user_name=user_name,password=ph.hash(password),user_type="organizer" )
    session.add(user)
    session.commit()
    session.close()

    return True

<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
# E2 - ADD PLAYER
def add_player(name, role, team, base_points):
    session = Session(engine)
    if role.lower() not in PLAYER_ROLES:
        session.close()
        return False
    player = Players( name=name, role=role.lower(), team=team, base_points=base_points )
    session.add(player)
    session.commit()
    player_id = player.id
    session.close()

    return {  "message": "Player added successfully", "player_id": player_id, "name": name, "role": role.lower(), "team": team,"base_points": base_points }

# PLAYER DETAILS
def player_details(player):
    return {"id": player.id,  "name": player.name, "role": player.role, "team": player.team, "base_points": player.base_points}


# E3 - GET ALL PLAYERS
def get_all_players(role=None, team=None):
    session = Session(engine)
    players = session.query(Players)
    if role:
        players = players.filter(Players.role == role.lower())
    if team:
        players = players.filter(Players.team == team)
    response = [ player_details(player)for player in players.all()]
    session.close()

    return response

<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
