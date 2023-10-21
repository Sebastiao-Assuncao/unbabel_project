from sqlalchemy import create_engine, MetaData
from databases import Database

# These variables should be more secure, leaving them here for simplicity
USERNAME = "unbabel_user"
PASSWORD = "unbabel_password"
HOST = "localhost"
PORT = "5432"
DB_NAME = "unbabel_db"

DATABASE_URL = f"postgresql+asyncpg://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

metadata = MetaData()

# Asynchronous database connection for FastAPI routes
database = Database(DATABASE_URL)

# Synchronous database connection for operations like table creation
engine = create_engine(DATABASE_URL.replace("+asyncpg", ""), echo=True)