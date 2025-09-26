"""
Task API endpoints
"""
from fastapi import APIRouter, Depends, Query
from typing import List

from ...models.task import Task, TaskCreate, TaskUpdate
from ...models.common import BaseResponse
from ...core.db import get_database
from ...core.errors import map_exception_to_http
from ...core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/", response_model=List[Task])
async def get_tasks():
    """Get all tasks (legacy implementation)"""
    try:
        db = await get_database()
        tasks_cursor = db.tasks.find().sort("created_at", -1)
        tasks = await tasks_cursor.to_list(100)
        
        result = []
        for task in tasks:
            task.pop('_id', None)
            if 'id' not in task:
                continue
            
            task_obj = Task(
                id=task['id'],
                meeting_id=task.get('meeting_id', ''),
                title=task.get('title', ''),
                description=task.get('description'),
                assignee=task.get('assignee'),
                priority=task.get('priority', 'medium'),
                status=task.get('status', 'pending'),
                due_date=task.get('due_date'),
                created_at=task.get('created_at'),
                updated_at=task.get('updated_at')
            )
            result.append(task_obj)
        
        logger.info("Tasks fetched via API", count=len(result))
        return result
        
    except Exception as e:
        logger.error("Failed to get tasks via API", error=str(e))
        raise map_exception_to_http(e)

@router.post("/", response_model=Task)
async def create_task(task: TaskCreate):
    """Create a new task (legacy implementation)"""
    try:
        db = await get_database()
        
        # Create task object
        task_obj = Task(
            meeting_id=task.meeting_id,
            title=task.title,
            description=task.description,
            assignee=task.assignee,
            priority=task.priority,
            due_date=task.due_date
        )
        
        result = await db.tasks.insert_one(task_obj.dict())
        logger.info("Task created via API", task_id=task_obj.id, title=task_obj.title)
        return task_obj
        
    except Exception as e:
        logger.error("Failed to create task via API", error=str(e))
        raise map_exception_to_http(e)

@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """Get a specific task"""
    try:
        db = await get_database()
        task_data = await db.tasks.find_one({"id": task_id})
        
        if not task_data:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_data.pop('_id', None)
        return Task(**task_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get task via API", task_id=task_id, error=str(e))
        raise map_exception_to_http(e)

@router.patch("/{task_id}", response_model=Task)
async def update_task(task_id: str, update_data: TaskUpdate):
    """Update a task"""
    try:
        db = await get_database()
        
        # Filter out None values
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        result = await db.tasks.update_one(
            {"id": task_id},
            {"$set": update_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Return updated task
        task_data = await db.tasks.find_one({"id": task_id})
        task_data.pop('_id', None)
        
        logger.info("Task updated via API", task_id=task_id)
        return Task(**task_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update task via API", task_id=task_id, error=str(e))
        raise map_exception_to_http(e)

@router.delete("/{task_id}")
async def delete_task(task_id: str) -> BaseResponse:
    """Delete a task"""
    try:
        db = await get_database()
        result = await db.tasks.delete_one({"id": task_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        
        logger.info("Task deleted via API", task_id=task_id)
        return BaseResponse(
            success=True,
            message="Task deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete task via API", task_id=task_id, error=str(e))
        raise map_exception_to_http(e)