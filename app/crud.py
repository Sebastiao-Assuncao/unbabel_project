from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, TranslationTask
from app.database import engine


# Create a new user in the database
async def create_user(username: str, hashed_password: str):
    # We are using sqlalchemy's AsyncSession instead of databases' raw SQL constructs to leverage the benefits of ORM
    async with AsyncSession(engine) as session:
        new_user = User(username=username, hashed_password=hashed_password)
        session.add(new_user)
        await session.commit()


# Get a user by username
async def get_user(username: str):
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).filter_by(username=username))
        return result.scalar()
    
# Create a new translation task
async def create_translation_task(user_id: int, source_language: str, target_language: str, text_to_translate: str):
    async with AsyncSession(engine) as session:
        new_translation_task = TranslationTask(user_id=user_id, source_language=source_language, target_language=target_language, text_to_translate=text_to_translate)
        session.add(new_translation_task)
        await session.commit()

# Get all translation tasks for a user
async def get_translation_tasks(username:str):
    
    # Fetch user 
    user = await get_user(username=username)
    if not user:
        return None
    
    # Fetch user's associated translations
    async with AsyncSession(engine) as session:
        result = await session.execute(select(TranslationTask).filter_by(user_id=user.id))
        return result.scalars().all()

async def get_translation_task_by_id(task_id: int):

    async with AsyncSession(engine) as session:
        result = await session.execute(select(TranslationTask).filter_by(id=task_id))
        return result.scalar()