from fastapi import APIRouter, HTTPException, Depends
from app.models import TranslationTaskIn, TranslationTaskOut, User, RatingIn, RatingOut
from app.crud import create_translation_task, get_translation_tasks, get_translation_task_by_id, create_translation_rating, get_rating_by_task_id, remove_rating
from app.api.auth.auth import get_current_user
from app.utils import mock_translate, translate_text
from typing import List

translation_router = APIRouter()

@translation_router.post("/tasks", response_model=TranslationTaskOut)
async def create_task(task: TranslationTaskIn, current_user: User = Depends(get_current_user)):
    """
    Creates a translation task.

    Args:
        task (TranslationTaskIn): The input data for the translation task.
        current_user (User): The current authenticated user.

    Returns:
        TranslationTaskOut: The created translation task.
    """
    # Used to save on API Costs
    #translated_text = mock_translate(task.text_to_translate, task.target_language)

    # Uses Google Cloud Translation API for translation
    source_language = task.source_language or None

    (translated_text, source_language) = translate_text(source_language, task.target_language, task.text_to_translate)

    return await create_translation_task(current_user.id, task, source_language, translated_text)

@translation_router.get("/tasks", response_model=List[TranslationTaskOut])
async def list_tasks(current_user: User = Depends(get_current_user)):
    """
    Lists the translation tasks associated with the current user.

    Args:
        current_user (User): The current authenticated user.

    Returns:
        List[TranslationTaskOut]: A list of translation tasks associated with the user.
    """

    return await get_translation_tasks(current_user.id)

@translation_router.get("/tasks/{task_id}", response_model=TranslationTaskOut)
async def get_task(task_id: int, current_user: User = Depends(get_current_user)):
    """
    Retrieves a translation task by its ID.

    Args:
        task_id (int): The ID of the translation task.
        current_user (User): The current authenticated user.

    Returns:
        TranslationTaskOut: The retrieved translation task.

    Raises:
        HTTPException: If the translation task is not found or the user is not authorized to access it.
    """

    task = await get_translation_task_by_id(task_id=task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Translation task not found")
    
    # Check if the task is owned by the current user
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this task")
    
    return task

@translation_router.post("/tasks/{task_id}/rate", response_model=RatingOut)
async def rate_task(task_id: int, rating: RatingIn, current_user: User = Depends(get_current_user)):
    """
    Rates a translation task.

    Args:
        task_id (int): The ID of the translation task to rate.
        rating (RatingIn): The input data for the rating.
        current_user (User): The current authenticated user.

    Returns:
        None

    Raises:
        HTTPException: If the translation task is not found, the user is not authorized to access it, or the task has already been rated.
    """
    task = await get_translation_task_by_id(task_id=task_id)

    # Check if task exists
    if not task:
        raise HTTPException(status_code=404, detail="Translation task not found")
    
    # Check if the task is owned by the current user
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this task")
    
    # Check if task has already been rated
    existing_rating = await get_rating_by_task_id(translation_id=task_id)
    if existing_rating:
        raise HTTPException(status_code=409, detail="Task has already been rated")
    
    return await create_translation_rating(rating=rating, task_id=task_id)

@translation_router.get("/tasks/{task_id}/rate")
async def get_rating(task_id: int, current_user: User = Depends(get_current_user)):
    """
    Retrieves the rating associated with a translation task.

    Args:
        task_id (int): The ID of the translation task.
        current_user (User): The current authenticated user.

    Returns:
        Optional[Rating]: The rating associated with the translation task, or None if not found.
    """

    return await get_rating_by_task_id(task_id)

@translation_router.delete("/tasks/{task_id}/rate")
async def delete_rating(task_id: int, current_user: User = Depends(get_current_user)):
    """
    Deletes the rating associated with a translation task.
    
    Args:
        task_id (int): The ID of the translation task.
        current_user (User): The current authenticated user.
    
    Returns:
        Dict[str, Union[str, int]]: A dictionary indicating the status and message of the deletion.
    
    Raises:
        HTTPException: If the rating is not found.
    """

    rating = await get_rating_by_task_id(task_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    await remove_rating(rating.id)
    return {"status": "success", "message": f"Successfully deleted rating with id {rating.id}"}
