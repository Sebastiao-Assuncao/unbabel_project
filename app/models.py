from pydantic import BaseModel
from sqlalchemy import Table, Column, Integer, String, MetaData
from app.database import metadata

class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("username", String(50), unique=True, index=True),
    Column("hashed_password", String)
)