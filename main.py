from datetime import datetime, timedelta
from secrets import token_urlsafe
from typing import Type

from bson import ObjectId
from pymongo import MongoClient

import jwt
from fastapi import FastAPI, Depends, HTTPException, status, Request, Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db.model import User

app = FastAPI()
auth = HTTPBasic()

client = MongoClient("mongodb://localhost:27017/")
db = client["CloudTech"]
users_collection = db["users"]

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def create_jwt_token(user_id: str):
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    token = jwt.encode(payload, "secret", algorithm="HS256")
    return token


def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
        user_id = payload["sub"]
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_user(credentials: HTTPBasicCredentials = Depends(auth)):
    user = users_collection.find_one({"username": credentials.username, "password": credentials.password})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


def create_database(user):
    dbname = f"db_{user['username']}_{token_urlsafe(8)}"
    dbpass = token_urlsafe(16)

    try:
        new_db = client[dbname]
        new_db["dummy_collection"].insert_one({"dummy": "data"})
        new_db.command("createUser", dbname, pwd=dbpass, roles=["readWrite"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database creation failed: {e}",
        )
    finally:
        client.close()

    return dbname, dbname, dbpass


@app.post("/register")
def register(credentials: HTTPBasicCredentials = Depends(auth)):
    if users_collection.find_one({"username": credentials.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    user = {"username": credentials.username, "password": credentials.password}
    users_collection.insert_one(user)

    return {"message": "User registered successfully"}


@app.post("/authorize")
def authorize(user: Type[User] = Depends(verify_user)):
    token = create_jwt_token(str(user["_id"]))
    return {"message": "User authorized successfully", "user_id": str(user["_id"]), "username": user["username"],
            "token": token}


@app.get("/create_database")
def create_database_for_user(token: str = Header(None)):
    user_id = verify_jwt_token(token)
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    dbname, dbuser, dbpass = create_database(user)
    return {"message": "Database created successfully", "database": dbname, "user": dbuser, "password": dbpass}


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
