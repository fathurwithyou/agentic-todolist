"""
Task API endpoints.
Handles task-related HTTP requests.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from datetime import datetime

from ..domains.task.models import GoogleTask, GoogleTaskList, TaskStatus, TaskPriority, ParsedTask
from ..domains.task.service import TaskService
from ..domains.task.repository import TaskRepository
from ..domains.llm.service import LLMService
from ..infrastructure.llm_repository import FileLLMRepository
from ..domains.llm.encryption import APIKeyEncryption
from ..infrastructure.auth_repository import FileAuthRepository
from .auth import get_current_user

logger = logging.getLogger(__name__)

# Initialize dependencies
auth_repository = FileAuthRepository()
task_repository = TaskRepository()
llm_repository = FileLLMRepository()
encryption = APIKeyEncryption()
llm_service = LLMService(llm_repository, encryption)
task_service = TaskService(task_repository, llm_service)

router = APIRouter(prefix="/tasks", tags=["tasks"])


class GoogleTaskResponse(BaseModel):
    """Response model for Google Task"""
    task_id: str
    title: str
    notes: Optional[str] = None
    status: str
    due: Optional[datetime] = None
    completed: Optional[datetime] = None
    priority: Optional[str] = None
    parent: Optional[str] = None
    web_view_link: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CreateGoogleTaskRequest(BaseModel):
    """Request to create a Google Task"""
    title: str = Field(..., description="Task title")
    notes: Optional[str] = Field(None, description="Task notes/description")
    due_date: Optional[str] = Field(None, description="Due date (YYYY-MM-DD)")
    due_time: Optional[str] = Field(None, description="Due time (HH:MM)")
    priority: Optional[str] = Field(None, description="Task priority (high/medium/low)")
    parent_task: Optional[str] = Field(None, description="Parent task ID for subtasks")
    list_id: str = Field("@default", description="Task list ID")


class UpdateGoogleTaskRequest(BaseModel):
    """Request to update a Google Task"""
    title: Optional[str] = Field(None, description="Task title")
    notes: Optional[str] = Field(None, description="Task notes/description")
    due_date: Optional[str] = Field(None, description="Due date (YYYY-MM-DD)")
    due_time: Optional[str] = Field(None, description="Due time (HH:MM)")
    priority: Optional[str] = Field(None, description="Task priority (high/medium/low)")
    completed: Optional[bool] = Field(None, description="Mark task as completed")


class GoogleTaskListResponse(BaseModel):
    """Response model for Google Task List"""
    list_id: str
    title: str
    task_count: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CreateGoogleTaskListRequest(BaseModel):
    """Request to create a Google Task List"""
    title: str = Field(..., description="Task list title")


class ParseTasksRequest(BaseModel):
    """Request to parse timeline text into tasks"""
    timeline_text: str = Field(..., description="Text to parse for tasks")
    list_id: str = Field("@default", description="Target task list ID")
    provider: Optional[str] = Field(None, description="LLM provider to use")
    model: Optional[str] = Field(None, description="Model to use")


class ParsedTaskResponse(BaseModel):
    """Response for parsed task"""
    title: str
    notes: Optional[str] = None
    due_date: Optional[str] = None
    due_time: Optional[str] = None
    priority: Optional[str] = None
    completed: bool = False


class CreateTasksResponse(BaseModel):
    """Response for creating tasks"""
    success: bool
    created_count: int
    total_count: int
    tasks: List[GoogleTaskResponse]
    provider_used: str
    model_used: str
    processing_time_ms: int


@router.get("/lists", response_model=List[GoogleTaskListResponse])
async def list_task_lists(user=Depends(get_current_user)):
    """List all task lists for the current user"""
    try:
        task_lists = task_service.get_user_task_lists(user.user_id)
        
        return [
            GoogleTaskListResponse(
                list_id=task_list.list_id,
                title=task_list.title,
                created_at=task_list.created_at,
                updated_at=task_list.updated_at
            )
            for task_list in task_lists
        ]
    except Exception as e:
        logger.error(f"Failed to list task lists: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lists", response_model=GoogleTaskListResponse)
async def create_task_list(
    request: CreateGoogleTaskListRequest, user=Depends(get_current_user)
):
    """Create a new task list"""
    try:
        task_list = task_service.create_task_list(user.user_id, request.title)
        
        if not task_list:
            raise HTTPException(status_code=400, detail="Failed to create task list")
        
        return GoogleTaskListResponse(
            list_id=task_list.list_id,
            title=task_list.title,
            created_at=task_list.created_at,
            updated_at=task_list.updated_at
        )
    except Exception as e:
        logger.error(f"Failed to create task list: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{list_id}", response_model=List[GoogleTaskResponse])
async def list_tasks(list_id: str, include_completed: bool = True, user=Depends(get_current_user)):
    """List tasks in a specific task list"""
    try:
        tasks = task_service.get_user_tasks(user.user_id, list_id, include_completed)
        
        return [
            GoogleTaskResponse(
                task_id=task.task_id,
                title=task.title,
                notes=task.notes,
                status=task.status.value,
                due=task.due,
                completed=task.completed,
                priority=task.priority.value if task.priority else None,
                parent=task.parent,
                web_view_link=task.web_view_link,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
            for task in tasks
        ]
    except Exception as e:
        logger.error(f"Failed to list tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{list_id}/tasks", response_model=GoogleTaskResponse)
async def create_task(
    list_id: str, request: CreateGoogleTaskRequest, user=Depends(get_current_user)
):
    """Create a new task in the specified list"""
    try:
        # Convert request to ParsedTask
        parsed_task = ParsedTask(
            title=request.title,
            notes=request.notes,
            priority=TaskPriority(request.priority) if request.priority else None,
            due_date=request.due_date,
            due_time=request.due_time,
            parent_task=request.parent_task
        )
        
        task = task_service.create_task_from_parsed(user.user_id, parsed_task, list_id)
        
        if not task:
            raise HTTPException(status_code=400, detail="Failed to create task")
        
        return GoogleTaskResponse(
            task_id=task.task_id,
            title=task.title,
            notes=task.notes,
            status=task.status.value,
            due=task.due,
            completed=task.completed,
            priority=task.priority.value if task.priority else None,
            parent=task.parent,
            web_view_link=task.web_view_link,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{list_id}/tasks/{task_id}", response_model=GoogleTaskResponse)
async def update_task(
    list_id: str, task_id: str, request: UpdateGoogleTaskRequest, user=Depends(get_current_user)
):
    """Update an existing task"""
    try:
        # Parse due datetime if provided
        due_datetime = None
        if request.due_date:
            try:
                if request.due_time:
                    time_str = request.due_time
                    if ":" in time_str and len(time_str) == 5:
                        time_str = f"{time_str}:00"
                    due_datetime = datetime.fromisoformat(f"{request.due_date}T{time_str}")
                else:
                    due_datetime = datetime.fromisoformat(f"{request.due_date}T23:59:59")
            except ValueError as e:
                logger.warning(f"Failed to parse due date: {e}")

        # Handle completion toggle
        if request.completed is not None:
            if request.completed:
                task = task_service.mark_task_completed(user.user_id, task_id, list_id)
            else:
                # Reopen task
                task = task_service.update_task(
                    user.user_id, task_id, list_id,
                    title=request.title,
                    notes=request.notes,
                    due=due_datetime,
                    priority=TaskPriority(request.priority) if request.priority else None
                )
                if task:
                    task.status = TaskStatus.NEEDS_ACTION
                    task.completed = None
                    task = task_service.repository.update_task(task)
        else:
            # Regular update
            task = task_service.update_task(
                user.user_id, task_id, list_id,
                title=request.title,
                notes=request.notes,
                due=due_datetime,
                priority=TaskPriority(request.priority) if request.priority else None
            )
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found or update failed")
        
        return GoogleTaskResponse(
            task_id=task.task_id,
            title=task.title,
            notes=task.notes,
            status=task.status.value,
            due=task.due,
            completed=task.completed,
            priority=task.priority.value if task.priority else None,
            parent=task.parent,
            web_view_link=task.web_view_link,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
    except Exception as e:
        logger.error(f"Failed to update task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{list_id}/tasks/{task_id}")
async def delete_task(list_id: str, task_id: str, user=Depends(get_current_user)):
    """Delete a task"""
    try:
        success = task_service.delete_task(user.user_id, task_id, list_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"success": True, "message": "Task deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{list_id}/parse", response_model=CreateTasksResponse)
async def create_tasks_from_timeline(
    list_id: str, request: ParseTasksRequest, user=Depends(get_current_user)
):
    """Parse timeline text and create tasks"""
    try:
        start_time = datetime.now()
        
        # Parse timeline using LLM (we'll update this to handle tasks)
        # For now, create a simple parser
        parsed_tasks = await _parse_timeline_for_tasks(
            request.timeline_text, 
            user.user_id,
            request.provider,
            request.model
        )
        
        # Create tasks
        created_tasks = task_service.create_tasks_from_parsed(
            user.user_id, parsed_tasks, list_id
        )
        
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return CreateTasksResponse(
            success=True,
            created_count=len(created_tasks),
            total_count=len(parsed_tasks),
            tasks=[
                GoogleTaskResponse(
                    task_id=task.task_id,
                    title=task.title,
                    notes=task.notes,
                    status=task.status.value,
                    due=task.due,
                    completed=task.completed,
                    priority=task.priority.value if task.priority else None,
                    parent=task.parent,
                    web_view_link=task.web_view_link,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                )
                for task in created_tasks
            ],
            provider_used=request.provider or "gemini",
            model_used=request.model or "gemini-2.0-flash-exp", 
            processing_time_ms=processing_time
        )
    except Exception as e:
        logger.error(f"Failed to create tasks from timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{list_id}/sync")
async def sync_tasks(list_id: str, user=Depends(get_current_user)):
    """Sync tasks with Google Tasks"""
    try:
        result = task_service.sync_with_google(user.user_id)
        return {
            "success": True,
            "message": f"Synced {result['synced_tasks']} tasks and {result['synced_lists']} lists"
        }
    except Exception as e:
        logger.error(f"Failed to sync tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _parse_timeline_for_tasks(timeline_text: str, user_id: str, 
                                   provider: Optional[str] = None, 
                                   model: Optional[str] = None) -> List[ParsedTask]:
    """Parse timeline text for tasks using LLM"""
    from ..domains.llm.models import ProviderType
    from ..providers.factory import LLMFactory
    from ..infrastructure.auth_repository import FileAuthRepository
    
    # Determine provider
    if provider:
        try:
            provider_enum = ProviderType(provider.lower())
        except ValueError:
            provider_enum = ProviderType.GEMINI
    else:
        provider_enum = ProviderType.GEMINI
    
    # Get API key
    api_key = llm_service.get_api_key(user_id, provider_enum)
    if not api_key:
        raise ValueError(f"No API key found for {provider_enum.value}")
    
    # Get user's system prompt
    auth_repository = FileAuthRepository()
    user = auth_repository.get_user(user_id)
    system_prompt = user.system_prompt if user else None
    
    # Get model name (use dynamic models for Gemini)
    if not model:
        if provider_enum == ProviderType.GEMINI:
            # Get dynamic models for Gemini
            dynamic_models = await llm_service.get_dynamic_provider_models(provider_enum, api_key)
            model_name = dynamic_models[0] if dynamic_models else llm_service.PROVIDERS[provider_enum].default_model
        else:
            static_models = llm_service.get_provider_models(provider_enum)
            model_name = static_models[0] if static_models else llm_service.PROVIDERS[provider_enum].default_model
    else:
        model_name = model
    
    # Create LLM provider
    llm_provider = LLMFactory.create_provider(
        provider_name=provider_enum.value, 
        api_key=api_key, 
        model_name=model_name
    )
    
    if not llm_provider:
        raise ValueError(f"Failed to create provider: {provider_enum.value}")
    
    await llm_provider.initialize()
    tasks = await llm_provider.parse_timeline_for_tasks(timeline_text, system_prompt)
    
    return tasks