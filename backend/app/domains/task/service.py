"""
Task domain service.
Handles task creation, management, and Google Tasks integration.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import GoogleTask, GoogleTaskList, ParsedTask, TaskStatus, TaskPriority
from .repository import TaskRepository
from .google_task_service import GoogleTaskService
from ..llm.service import LLMService

logger = logging.getLogger(__name__)


class TaskService:
    """
    Task domain service.
    Handles task operations and Google Tasks integration.
    """

    def __init__(self, repository: TaskRepository, llm_service: LLMService):
        self.repository = repository
        self.llm_service = llm_service

    def create_task_from_parsed(self, user_id: str, parsed_task: ParsedTask, 
                               list_id: str = "@default") -> Optional[GoogleTask]:
        """Create a Google Task from parsed task data"""
        from ...infrastructure.auth_repository import FileAuthRepository
        
        # Get user and create Google Task
        auth_repository = FileAuthRepository()
        user = auth_repository.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        google_task_service = GoogleTaskService(user, auth_repository)

        # Parse due datetime if provided
        due_datetime = None
        if parsed_task.due_date:
            try:
                if parsed_task.due_time:
                    # Handle HH:MM format
                    time_str = parsed_task.due_time
                    if ":" in time_str and len(time_str) == 5:
                        time_str = f"{time_str}:00"
                    due_datetime = datetime.fromisoformat(f"{parsed_task.due_date}T{time_str}")
                else:
                    due_datetime = datetime.fromisoformat(f"{parsed_task.due_date}T23:59:59")
            except ValueError as e:
                logger.warning(f"Failed to parse due date: {e}")

        # Create task in Google Tasks
        google_task = google_task_service.create_task(
            title=parsed_task.title,
            notes=parsed_task.notes or "",
            due=due_datetime,
            parent=parsed_task.parent_task,
            list_id=list_id
        )

        if not google_task:
            raise ValueError(f"Failed to create Google Task: {parsed_task.title}")

        # Convert to our task model and save locally
        task = GoogleTask(
            task_id=google_task["id"],
            user_id=user_id,
            title=parsed_task.title,
            notes=parsed_task.notes or "",
            status=TaskStatus.COMPLETED if parsed_task.completed else TaskStatus.NEEDS_ACTION,
            due=due_datetime,
            completed=datetime.now() if parsed_task.completed else None,
            priority=parsed_task.priority,
            parent=parsed_task.parent_task,
            google_task_id=google_task["id"],
            etag=google_task.get("etag"),
            self_link=google_task.get("selfLink"),
            web_view_link=google_task.get("webViewLink")
        )

        # Save to local repository
        saved_task = self.repository.save_task(task)
        logger.info(f"Created Google Task {task.task_id} for user {user_id}")

        return saved_task

    def create_tasks_from_parsed(self, user_id: str, parsed_tasks: List[ParsedTask], 
                                list_id: str = "@default") -> List[GoogleTask]:
        """Create multiple tasks from parsed data"""
        created_tasks = []

        for parsed_task in parsed_tasks:
            try:
                task = self.create_task_from_parsed(user_id, parsed_task, list_id)
                if task:
                    created_tasks.append(task)
            except Exception as e:
                logger.error(f"Failed to create task '{parsed_task.title}': {e}")

        logger.info(f"Created {len(created_tasks)}/{len(parsed_tasks)} tasks for user {user_id}")
        return created_tasks

    def get_user_tasks(self, user_id: str, list_id: Optional[str] = None, 
                      include_completed: bool = True) -> List[GoogleTask]:
        """Get all tasks for a user"""
        tasks = self.repository.get_user_tasks(user_id, list_id)
        
        if not include_completed:
            tasks = [task for task in tasks if task.status != TaskStatus.COMPLETED]
        
        return tasks

    def mark_task_completed(self, user_id: str, task_id: str, list_id: str = "@default") -> Optional[GoogleTask]:
        """Mark a task as completed"""
        from ...infrastructure.auth_repository import FileAuthRepository
        
        auth_repository = FileAuthRepository()
        user = auth_repository.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        google_task_service = GoogleTaskService(user, auth_repository)
        
        # Update in Google Tasks
        updated_google_task = google_task_service.mark_task_completed(task_id, list_id)
        if not updated_google_task:
            return None

        # Update local copy
        task = self.repository.get_task(task_id)
        if task:
            task.status = TaskStatus.COMPLETED
            task.completed = datetime.now()
            task.updated_at = datetime.now()
            return self.repository.update_task(task)
        
        return None

    def update_task(self, user_id: str, task_id: str, list_id: str = "@default", 
                   title: Optional[str] = None, notes: Optional[str] = None,
                   due: Optional[datetime] = None, priority: Optional[TaskPriority] = None) -> Optional[GoogleTask]:
        """Update a task"""
        from ...infrastructure.auth_repository import FileAuthRepository
        
        auth_repository = FileAuthRepository()
        user = auth_repository.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        google_task_service = GoogleTaskService(user, auth_repository)
        
        # Update in Google Tasks
        updated_google_task = google_task_service.update_task(
            task_id=task_id, 
            list_id=list_id,
            title=title,
            notes=notes,
            due=due
        )
        
        if not updated_google_task:
            return None

        # Update local copy
        task = self.repository.get_task(task_id)
        if task:
            if title is not None:
                task.title = title
            if notes is not None:
                task.notes = notes
            if due is not None:
                task.due = due
            if priority is not None:
                task.priority = priority
            task.updated_at = datetime.now()
            return self.repository.update_task(task)
        
        return None

    def delete_task(self, user_id: str, task_id: str, list_id: str = "@default") -> bool:
        """Delete a task"""
        from ...infrastructure.auth_repository import FileAuthRepository
        
        auth_repository = FileAuthRepository()
        user = auth_repository.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        google_task_service = GoogleTaskService(user, auth_repository)
        
        # Delete from Google Tasks
        success = google_task_service.delete_task(task_id, list_id)
        if success:
            # Delete from local repository
            self.repository.delete_task(task_id)
        
        return success

    def create_task_list(self, user_id: str, title: str) -> Optional[GoogleTaskList]:
        """Create a new task list"""
        from ...infrastructure.auth_repository import FileAuthRepository
        
        auth_repository = FileAuthRepository()
        user = auth_repository.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        google_task_service = GoogleTaskService(user, auth_repository)
        
        # Create in Google Tasks
        google_list = google_task_service.create_task_list(title)
        if not google_list:
            return None

        # Save locally
        task_list = GoogleTaskList(
            list_id=google_list["id"],
            user_id=user_id,
            title=title,
            google_list_id=google_list["id"],
            etag=google_list.get("etag"),
            self_link=google_list.get("selfLink")
        )

        saved_list = self.repository.save_task_list(task_list)
        logger.info(f"Created task list {task_list.list_id} for user {user_id}")

        return saved_list

    def get_user_task_lists(self, user_id: str) -> List[GoogleTaskList]:
        """Get all task lists for a user"""
        return self.repository.get_user_task_lists(user_id)

    def sync_with_google(self, user_id: str) -> Dict[str, int]:
        """Sync local tasks with Google Tasks"""
        from ...infrastructure.auth_repository import FileAuthRepository
        
        auth_repository = FileAuthRepository()
        user = auth_repository.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        google_task_service = GoogleTaskService(user, auth_repository)
        
        synced_tasks = 0
        synced_lists = 0
        
        # Sync task lists
        google_lists = google_task_service.list_task_lists()
        for google_list in google_lists:
            list_id = google_list["id"]
            existing_list = self.repository.get_task_list(list_id)
            
            if not existing_list:
                # Create new local task list
                task_list = GoogleTaskList(
                    list_id=list_id,
                    user_id=user_id,
                    title=google_list["title"],
                    google_list_id=list_id,
                    etag=google_list.get("etag"),
                    self_link=google_list.get("selfLink")
                )
                self.repository.save_task_list(task_list)
                synced_lists += 1
            
            # Sync tasks in this list
            google_tasks = google_task_service.list_tasks(list_id, show_completed=True)
            for google_task in google_tasks:
                task_id = google_task["id"]
                existing_task = self.repository.get_task(task_id)
                
                if not existing_task:
                    # Create new local task
                    task = GoogleTask(
                        task_id=task_id,
                        user_id=user_id,
                        title=google_task["title"],
                        notes=google_task.get("notes"),
                        status=TaskStatus(google_task.get("status", "needsAction")),
                        due=datetime.fromisoformat(google_task["due"].replace('Z', '+00:00')) if google_task.get("due") else None,
                        completed=datetime.fromisoformat(google_task["completed"].replace('Z', '+00:00')) if google_task.get("completed") else None,
                        parent=google_task.get("parent"),
                        position=google_task.get("position"),
                        google_task_id=task_id,
                        etag=google_task.get("etag"),
                        self_link=google_task.get("selfLink"),
                        web_view_link=google_task.get("webViewLink")
                    )
                    self.repository.save_task(task)
                    synced_tasks += 1

        return {"synced_tasks": synced_tasks, "synced_lists": synced_lists}