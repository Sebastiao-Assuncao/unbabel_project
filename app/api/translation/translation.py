from fastapi import APIRouter, HTTPException, Depends
from app.models import TranslationTask, TranslationTaskIn, TranslationTaskOut, User, RatingIn
from app.crud import create_translation_task, get_translation_tasks, get_translation_task_by_id, create_translation_rating, get_rating_by_task_id, delete_rating
from app.api.auth.auth import get_current_user
from typing import List

translation_router = APIRouter()

@translation_router.post("/tasks", response_model=TranslationTaskOut)
async def create_task(task: TranslationTaskIn, current_user: User = Depends(get_current_user)):
    return await create_translation_task(current_user.id, task)

@translation_router.get("/tasks", response_model=List[TranslationTaskOut])
async def list_tasks(current_user: User = Depends(get_current_user)):
    return await get_translation_tasks(current_user.id)

@translation_router.get("/tasks/{task_id}", response_model=TranslationTaskOut)
async def get_task(task_id: int, current_user: User = Depends(get_current_user)):
    task = await get_translation_task_by_id(task_id=task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Translation task not found")
    
    # Check if the task is owned by the current user
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this task")
    
    return task

@translation_router.post("/tasks/{task_id}/rate")
async def rate_task(task_id: int, rating: RatingIn, current_user: User = Depends(get_current_user)):
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

# @translation_router.get("tasks/{task_id}/rate")
# async def get_rating(task_id: int, current_user: User = Depends(get_current_user)):
#     return await get_rating_by_task_id(task_id)

@translation_router.delete("/tasks/{task_id}/rate")
async def delete_rating(task_id: int, current_user: User = Depends(get_current_user)):
    rating = await get_rating_by_task_id(task_id)
    
    # TODO: This is happening even when there is a rating
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    return await delete_rating(rating.id)
