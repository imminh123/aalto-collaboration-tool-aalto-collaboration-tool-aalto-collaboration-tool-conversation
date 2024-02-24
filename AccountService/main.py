from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import Optional
from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from database import AsyncSessionLocal, Base, engine, User
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows only specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# async def get_db():
#     async with AsyncSessionLocal() as session:
#         yield session

# @app.on_event("startup")
# async def startup():
#     async with engine.begin() as conn:
#         # Optional: Create tables if not exist (for demonstration)
#         await conn.run_sync(Base.metadata.create_all)

# User model
class User(BaseModel):
    username: str
    # disabled: Optional[bool] = None
    user_id: str

# User model in DB with hashed password
class UserInDB(User):
    hashed_password: str
    user_id: str

# User registration model
class UserRegister(BaseModel):
    username: str
    password: str

# Login model
class UserLogin(BaseModel):
    username: str
    password: str

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user storage
fake_users_db = {}

# Utility functions
def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Registration endpoint
@app.post("/register/", response_model=User)
async def register(user: UserRegister):
    print("Test")
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    user_id = str(uuid.uuid4())
    fake_users_db[user.username] = {
        "username": user.username,
        "hashed_password": hashed_password,
        "user_id": user_id,
        # "disabled": False,
    }
    # return "test"
    return {
        "username": user.username,
        # "disabled": False,
        "user_id": user_id,
    }

# Simple login endpoint
@app.post("/login")
async def login(user_login: UserLogin):
    user = get_user(fake_users_db, user_login.username)
    if not user or not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    # return {"message": "Login successful for user: {}".format(user.username)}
    return {
        "username": user.username,
        "user_id": user.user_id,
    }

@app.get("/users")
async def listUser():
    users_list = [{"username": value["username"], "user_id": value["user_id"]} for key, value in fake_users_db.items()]
    return users_list
