from app.database import sync_engine
from app.models import Base

Base.metadata.create_all(bind=sync_engine)