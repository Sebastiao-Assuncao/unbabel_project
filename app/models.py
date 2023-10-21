from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from app.database import metadata

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String)

class TranslationTask(Base):
    __tablename__ = 'translation_tasks'

    id = Column(Integer, Sequence('translation_task_id_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    source_language = Column(String(5), nullable=False)
    target_language = Column(String(5), nullable=False)
    text_to_translate = Column(String, nullable=False)
    # Nullable since upon creation, translated text will not yet exist
    translated_text = Column(String)

class Token(BaseModel):
    access_token: str
    token_type: str