from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, TranslationTaskIn, TranslationTaskOut, TranslationTask, BlacklistedToken, Rating, RatingIn, RatingOut
from app.database import async_engine


async def create_user(username: str, hashed_password: str):
    """
    Creates a new user with the given username and hashed password.

    Args:
        username (str): The username of the user.
        hashed_password (str): The hashed password of the user.

    Returns:
        None
    """
    # We are using sqlalchemy's AsyncSession instead of databases' raw SQL constructs to leverage the benefits of ORM
    async with AsyncSession(async_engine) as session:
        new_user = User(username=username, hashed_password=hashed_password)
        session.add(new_user)
        await session.commit()


async def get_user(username: str):
    """
    Retrieves a user with the given username.

    Args:
        username (str): The username of the user to retrieve.

    Returns:
        Optional[User]: The user with the given username, or None if not found.
    """
    async with AsyncSession(async_engine) as session:
        result = await session.execute(select(User).filter_by(username=username))
        return result.scalar()

# Get a user by ID
async def get_user_by_id(user_id: int):
    """
    Retrieves a user with the given user ID.

    Args:
        user_id (int): The ID of the user to retrieve.

    Returns:
        Optional[User]: The user with the given ID, or None if not found.
    """
    async with AsyncSession(async_engine) as session:
        result = await session.execute(select(User).filter_by(id=user_id))
        return result.scalar()
    
async def blacklist_token(token: str):
    """
    Blacklists a token.

    Args:
        token (str): The token to be blacklisted.

    Returns:
        None
    """
    async with AsyncSession(async_engine) as session:
        new_token = BlacklistedToken(token=token)
        session.add(new_token)
        await session.commit()

async def is_token_blacklisted(token: str):
    """
    Checks if a token is blacklisted.

    Args:
        token (str): The token to check.

    Returns:
        bool: True if the token is blacklisted, False otherwise.
    """
    async with AsyncSession(async_engine) as session:
        result = await session.execute(select(BlacklistedToken).filter_by(token=token))
        return bool(result.scalar())

    
# Create a new translation task
async def create_translation_task(user_id: int, task: TranslationTaskIn, source: str, translated_text: str):
    """
    Creates a translation task for a user.

    Args:
        user_id (int): The ID of the user.
        task (TranslationTaskIn): The input data for the translation task.

    Returns:
        TranslationTaskOut: The created translation task.

    """
    async with AsyncSession(async_engine) as session:
        new_translation_task = TranslationTask(user_id=user_id, source_language=source,
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

async def get_translation_tasks(user_id: int):
    """
    Retrieves all the translation tasks associated with a user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        Optional[List[TranslationTask]]: A list of translation tasks associated with the user, or None if the user does not exist.
    """
    # Fetch user 
    user = await get_user_by_id(user_id=user_id)
    if not user:
        return None
    
    # Fetch user's associated translations
    async with AsyncSession(async_engine) as session:
        result = await session.execute(select(TranslationTask).filter_by(user_id=user.id))
        return result.scalars().all()

async def get_translation_task_by_id(task_id: int):
    """
    Retrieves a translation task with the given ID.

    Args:
        task_id (int): The ID of the translation task to retrieve.

    Returns:
        Optional[TranslationTask]: The translation task with the given ID, or None if not found.
    """
    async with AsyncSession(async_engine) as session:
        result = await session.execute(select(TranslationTask).filter_by(id=task_id))
        return result.scalar()
    
    
async def create_translation_rating(rating: RatingIn, task_id: int):
    """
    Creates a rating for a translation task.

    Args:
        rating (RatingIn): The input data for the rating.
        task_id (int): The ID of the translation task.

    Returns:
        RatingOut: The created rating.
    """
    async with AsyncSession(async_engine) as session:
        new_rating = Rating(translation_id=task_id, rating=rating.rating, feedback=rating.feedback)

        session.add(new_rating)
        await session.commit()
        await session.refresh(new_rating)

        return RatingOut(
            id=new_rating.id,
            rating=new_rating.rating,
            feedback=new_rating.feedback
        )
    
async def get_rating_by_task_id(translation_id: int):
    """
    Retrieves a rating associated with a translation task.

    Args:
        translation_id (int): The ID of the translation task.

    Returns:
        Optional[Rating]: The rating associated with the translation task, or None if not found.
    """
    async with AsyncSession(async_engine) as session:
        result = await session.execute(select(Rating).filter_by(translation_id=translation_id))
        return result.scalar()

async def remove_rating(id: int):
    """
    Deletes a rating with the given ID.

    Args:
        id (int): The ID of the rating to delete.

    Returns:
        None
    """
    async with AsyncSession(async_engine) as session:
        result = await session.execute(select(Rating).filter_by(id=id))
        rating_to_delete = result.scalar()

        await session.delete(rating_to_delete)
        await session.commit()

