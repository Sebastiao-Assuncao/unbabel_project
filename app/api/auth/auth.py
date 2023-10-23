from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.models import UserIn, Token
from app.crud import create_user, get_user, blacklist_token
import datetime
import bcrypt
import jwt

auth_router = APIRouter()

# For simplicity, we leave SECRET_KEY and ALGORITHM here unsafe
SECRET_KEY = "my_secret_key"
ALGORITHM = "HS256"

access_token_jwt_subject = "access"

# Instance of OAuth2PasswordBearer class to get token from header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@auth_router.post("/register")
async def register(user: UserIn):
    # Check if user already exists
    existing_user = await get_user(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hash the password
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    # Store in db
    await create_user(user.username, hashed_password.decode('utf-8'))

    return {"status": "success", "username": user.username}

@auth_router.post("/login", response_model=Token)
async def login(user: UserIn):
    # Fetch user from the database
    db_user = await get_user(user.username)

    # Check if user exists
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Verify the hashed password
    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # We add a unique timestamp to allow for multi-sessions after logging out (and blackmailing the token)
    current_time = datetime.datetime.now()

    # Generate JWT token
    access_token = jwt.encode({"sub": user.username, "iat": current_time}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    # Blacklist the token
    await blacklist_token(token)
    return {"status": "success", "message": "Successfully logged out"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Decode the JWT token and return the current user
    """
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid Credentials")

        # Fetch the user from our database
        user = await get_user(username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail="Invalid credentials") from e