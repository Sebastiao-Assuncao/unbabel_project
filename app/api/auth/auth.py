from fastapi import APIRouter, HTTPException, Depends
from app.models import User, Token
from app.database import users_db
import bcrypt
import jwt

auth_router = APIRouter()

# For simplicity, we leave SECRET_KEY and ALGORITHM here unsafe
SECRET_KEY = "my_secret_key"
ALGORITHM = "HS256"

access_token_jwt_subject = "access"

@auth_router.post("/register")
def register(user: User):
    # Check if user already exists
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hash the password
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    # Store in mock db
    users_db[user.username] = {
        "hashed_password" : hashed_password
    } 

    return {"status": "success", "username": user.username}

@auth_router.post("/login", response_model=Token)
def login(user: User):

    # Check if username exists
    if user.username not in users_db:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Verify password
    if not bcrypt.checkpw(user.password.encode('utf-8'), users_db[user.username]["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Generate JWT token
    access_token = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}
