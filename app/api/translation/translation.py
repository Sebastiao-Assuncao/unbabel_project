from fastapi import APIRouter, HTTPException, Depends
from app.models import TranslationTask, TranslationTaskIn, TranslationTaskOut, User
from app.crud import create_translation_task, get_translation_tasks, get_translation_task_by_id
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