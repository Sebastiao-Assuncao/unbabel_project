from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, TranslationTaskIn, TranslationTaskOut, TranslationTask, BlacklistedToken
from app.database import async_engine
from app.utils import mock_translate


# Create a new user in the database
async def create_user(username: str, hashed_password: str):
    # We are using sqlalchemy's AsyncSession instead of databases' raw SQL constructs to leverage the benefits of ORM
    async with AsyncSession(async_engine) as session:
        new_user = User(username=username, hashed_password=hashed_password)
        session.add(new_user)
        await session.commit()


# Get a user by username
async def get_user(username: str):
    async with AsyncSession(async_engine) as session:
        result = await session.execute(select(User).filter_by(username=username))
        return result.scalar()

# Get a user by ID
async def get_user_by_id(user_id: int):
    async with AsyncSession(async_engine) as session:
        result = await session.execute(select(User).filter_by(id=user_id))
        return result.scalar()
    
async def blacklist_token(token: str):
    async with AsyncSession(async_engine) as session:
        new_token = BlacklistedToken(token=token)
        session.add(new_token)
        await session.commit()

async def is_token_blacklisted(token: str):
    async with AsyncSession(async_engine) as session:
        result = await session.execute(select(BlacklistedToken).filter_by(token=token))
        return bool(result.scalar())

    
# Create a new translation task
async def create_translation_task(user_id: int, task: TranslationTaskIn):
    async with AsyncSession(async_engine) as session:
        translated_text = mock_translate(task.text_to_translate, task.target_language)
        new_translation_task = TranslationTask(user_id=user_id, source_language=task.source_language,
                                               target_language=task.target_language, text_to_translate=task.text_to_translate, translated_text=translated_text)
        session.add(new_translation_task)
        await session.commit()
        await session.refresh(new_translation_task)  # Refresh to get any updated attributes from the DB


        # Convert the ORM object to the Pydantic model, TranslationTaskOut.from_orm is depracated
        return TranslationTaskOut(
            id=new_translation_task.id,
            user_id=new_translation_task.user_id,
            source_language=new_translation_task.source_language,
            target_language=new_translation_task.target_language,
            text_to_translate=new_translation_task.text_to_translate,
            translated_text=new_translation_task.translated_text
        )

# Get all translation tasks for a user
async def get_translation_tasks(user_id: int):
    
    # Fetch user 
    user = await get_user_by_id(user_id=user_id)
    if not user:
        return None
    
    # Fetch user's associated translations
    async with AsyncSession(async_engine) as session:
        result = await session.execute(select(TranslationTask).filter_by(user_id=user.id))
        return result.scalars().all()

async def get_translation_task_by_id(task_id: int):
    async with AsyncSession(async_engine) as session:
        result = await session.execute(select(TranslationTask).filter_by(id=task_id))
        return result.scalar()