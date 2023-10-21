from sqlalchemy import create_engine, MetaData
from databases import Database

DATABASE_URL = "postgresql+asyncpg://<username>:<password>@<host>:<port>/<dbname>"

metadata = MetaData()
database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL.replace("+asyncpg", ""), echo=True)

# Mock database for users
users_db = {}