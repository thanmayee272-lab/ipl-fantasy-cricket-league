from sqlalchemy import Integer, String, Column, create_engine
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Database
DB_PATH = "ipl_fantasy.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True)
    user_name = Column(String)
    password = Column(String)
    role = Column(String)
    
# E2 - Players table
class Players(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)
    team = Column(String)
    base_points = Column(Integer)


Base.metadata.create_all(bind=engine)    


Base.metadata.create_all(bind=engine)
ACCESS_TOKEN_EXPIRY = 15
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60

SECRET_KEY = "secret1234"
ALGORITHM = "HS256"

def create_token(username, role, token_type):

    token_minutes = ACCESS_TOKEN_EXPIRY

    if token_type == "refresh": token_minutes = REFRESH_TOKEN_EXPIRY
    payload = {"username": username, "role": role,"token_type": token_type,"exp": datetime.now(timezone.utc) + timedelta(minutes=token_minutes) }
    token = jwt.encode( payload=payload, key=SECRET_KEY,algorithm=ALGORITHM)
    return token

def verify_token(token, token_type):
    try:
        payload = jwt.decode(  token, SECRET_KEY, algorithms=[ALGORITHM])

    except jwt.PyJWTError:
        return None
    if payload.get("token_type") != token_type:
        return None

    return payload

def refresh_access_token(refresh_token):

    payload = verify_token(token=refresh_token,token_type="refresh" )
    if not payload:
        return None
    username = payload.get("username")
    if not username:
        return None
    session = Session(engine)

    try:
        user = session.query(User).filter_by( user_name=username
        ).first()
        if user is None:
            return None
        access_token = create_token(username=user.user_name, role=user.role, token_type="access" )
        return { "access_token": access_token }

    finally:
        session.close()
        
def add_player(name, role, team, base_points):
    session = Session(engine)

    try:
        player = Players(name=name,  role=role ,  team=team, base_points=base_points )

        session.add(player)
        session.commit()
        session.refresh(player)
        return {
            "message": "Player added successfully",
            "player_id": player.id,
            "name": player.name,
            "role": player.role,
            "team": player.team,
            "base_points": player.base_points
        }

    finally:
        session.close()
