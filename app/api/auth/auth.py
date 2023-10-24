from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from app.models import UserIn, UserOut, Token
from app.crud import create_user, get_user, blacklist_token
from datetime import datetime, timedelta
import bcrypt
import jwt

auth_router = APIRouter()

# For simplicity, we leave SECRET_KEY and ALGORITHM here unsafe
SECRET_KEY = "my_secret_key"
ALGORITHM = "HS256"

access_token_jwt_subject = "access"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Instance of HTTPBearer to get token
bearer = HTTPBearer()

# TODO: Google-Translate library

@auth_router.post("/register", response_model=UserOut)
async def register(user: UserIn):
    """
    Registers a new user.

    Args:
        user (UserIn): The input data for the new user.

    Returns:
        UserOut: The registered user.

    Raises:
        HTTPException: If the username is already registered.
    """
    # Check if user already exists
    existing_user = await get_user(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hash the password
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    # Store in db
    await create_user(user.username, hashed_password.decode('utf-8'))

    return UserOut(username=user.username)

@auth_router.post("/login", response_model=Token)
async def login(user: UserIn):
    """
    Logs in a user and returns an access token.

    Args:
        user (UserIn): The input data for the user login.

    Returns:
        Token: The access token.

    Raises:
        HTTPException: If the username or password is incorrect.
    """
    # Fetch user from the database
    db_user = await get_user(user.username)

    # Check if user exists
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Verify the hashed password
    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Expiration included for added security. Re-login required.
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Generate JWT token
    access_token = jwt.encode({"sub": user.username, "exp": expire }, SECRET_KEY, algorithm=ALGORITHM)
    return Token(access_token=access_token, token_type="Bearer")

@auth_router.post("/logout")
async def logout(token: str = Depends(bearer)):
    """
    Logs out a user by blacklisting the token.

    Args:
        token (str): The access token.

    Returns:
        Dict[str, str]: A dictionary indicating the status and message of the logout.
    """
    # Blacklist the token
    token_str = token.credentials
    await blacklist_token(token_str)
    return {"status": "success", "message": "Successfully logged out."}

async def get_current_user(token: str = Depends(bearer)):
    """
    Retrieves the current authenticated user based on the provided token.

    Args:
        token (str): The access token.

    Returns:
        User: The current authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    try:
        # Decode the token
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid Credentials")

        # Fetch the user from our database
        user = await get_user(username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail="Invalid credentials. Try logging in again") from e