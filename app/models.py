from pydantic import BaseModel, validator
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
    translated_text = Column(String, nullable=False)

class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, Sequence('ratings_id_seq'), primary_key=True)
    translation_id = Column(Integer, ForeignKey('translation_tasks.id'))
    rating = Column(Integer, nullable=False)
    feedback = Column(String)

    @validator('rating')
    def check_rating(cls, rating):
        if rating < 1 or rating > 5:
            raise ValueError("Rating is invalid. Insert a number between 1 and 5.")
        
        return rating

# Used to implement the logout function.
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
    source_language: Optional[str] = None
    target_language: str
    text_to_translate: str

class TranslationTaskOut(TranslationTaskIn):
    id: int
    translated_text: str

class RatingIn(BaseModel):
    rating: int
    feedback: Optional[str] = None

class RatingOut(RatingIn):
    id: int