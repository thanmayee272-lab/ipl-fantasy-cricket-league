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
    base_points = Column(Integer)

class FantasyTeams(Base):
    __tablename__ = "fantasy_teams"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)

class Matches(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
    match_name = Column(String)
    match_date = Column(Date)
    deadline = Column(DateTime)                   

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


# A2
def verify_login(username, password):
    session = Session(engine)
    user = session.query(Users).filter_by(user_name=username).first()
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
    access_token = create_token(username=username, token_type="access", user_type=user_type)
    refresh_token = create_token(username=username, token_type="refresh", user_type=user_type)
    return {"access_token": access_token, "refresh_token": refresh_token}

def create_token(username, token_type, user_type="user"):
    time = ACCESS_TOKEN_EXPIRY
    if token_type == "refresh":
        time = REFRESH_TOKEN_EXPIRY
    payload = {"username": username, "token_type": token_type, "exp": datetime.now(timezone.utc) + timedelta(minutes=time), "user_type": user_type}
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return token

