from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional


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
    translated_text = Column(String, nullable=False)

class BlacklistedToken(Base):
    __tablename__ = 'blacklisted_tokens'

    id = Column(Integer, Sequence('blacklisted_token_id_seq'), primary_key=True)
    token = Column(String, unique=True, index=True, nullable=False)


class Token(BaseModel):
    access_token: str
    token_type: str


# Pydantic models for request validation and response formatting
class UserIn(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str

class TranslationTaskIn(BaseModel):
    source_language: str
    target_language: str
    text_to_translate: str

class TranslationTaskOut(TranslationTaskIn):
    id: int
    translated_text: Optional[str]