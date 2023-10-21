from fastapi import APIRouter, HTTPException, Depends
from app.models import User, Token
from app.database import users_db
from app.crud import create_user, get_user
import bcrypt
import jwt

auth_router = APIRouter()

# For simplicity, we leave SECRET_KEY and ALGORITHM here unsafe
SECRET_KEY = "my_secret_key"
ALGORITHM = "HS256"

access_token_jwt_subject = "access"

@auth_router.post("/register")
async def register(user: User):
    # Check if user already exists
    existing_user = await get_user(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hash the password
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    # Store in mock db
    await create_user(user.username, hashed_password.decode('utf-8'))

    return {"status": "success", "username": user.username}

@auth_router.post("/login", response_model=Token)
async def login(user: User):
    # Fetch user from the database
    db_user = await get_user(user.username)

    # Check if user exists
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Verify the hashed password
    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Generate JWT token
    access_token = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}
