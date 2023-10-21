from fastapi import FastAPI, HTTPException, Depends
from .auth import auth_router
from app.database import users_db

app = FastAPI()

app.include_router(auth_router)