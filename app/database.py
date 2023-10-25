from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import MetaData, create_engine
from databases import Database
import os


# These variables should be more secure, leaving them here for simplicity

USERNAME = os.environ.get("POSTGRES_USER")
PASSWORD = os.environ.get("POSTGRES_PASSWORD")
DB_NAME = os.environ.get("POSTGRES_DB")

# These have to be changed when running init_db.py
HOST = "db"
PORT = "5432"

DATABASE_URL = f"postgresql+asyncpg://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

metadata = MetaData()

# Asynchronous engine for the main application
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Synchronous engine for administrative tasks
sync_engine = create_engine(DATABASE_URL.replace("+asyncpg", ""), echo=True)


# Useful connection for asynch raw SQL queries (might be useful later)
database = Database(DATABASE_URL)