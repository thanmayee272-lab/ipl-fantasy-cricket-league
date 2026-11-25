from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
import functions

app = FastAPI()

class UserLogin(BaseModel):
    user_name: str = Field(min_length=1)
    password: str = Field(min_length=1)

class OrganizerRegister(BaseModel):
    user_name: str = Field(min_length=3)
    password: str = Field(min_length=6)

# A2
@app.post("/auth/login")
def login(user: UserLogin):
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

# E1
@app.post("/admin/organizers")
def create_organizer(user: OrganizerRegister, token=Header(None)):
    check_role(token, ["admin"])
    if functions.create_organizer(user_name=user.user_name, password=user.password):
        return {"message": "Organizer created successfully"}
    raise HTTPException(status_code=409, detail="User already exists")
