"""
Google Tasks service.
Handles direct integration with Google Tasks API.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..auth.models import User
from ...infrastructure.auth_repository import FileAuthRepository
from .models import GoogleTask, GoogleTaskList, TaskStatus, TaskPriority

logger = logging.getLogger(__name__)


class GoogleTaskService:
    """Service for Google Tasks API operations"""

    def __init__(self, user: User, auth_repository: FileAuthRepository):
        self.user = user
        self.auth_repository = auth_repository
        self._service = None

    def _get_tasks_service(self):
        """Get authenticated Google Tasks service"""
        if self._service is None:
            from googleapiclient.discovery import build
            
            # Get user's Google credentials
            creds = self.auth_repository.get_user_credentials(self.user.user_id)
            if not creds or not creds.valid:
                raise ValueError("User has no valid Google credentials")
            
            self._service = build('tasks', 'v1', credentials=creds)
            logger.info("Google Tasks service initialized")
        
        return self._service

    def list_task_lists(self) -> List[Dict[str, Any]]:
        """List all task lists for the user"""
        try:
            service = self._get_tasks_service()
            result = service.tasklists().list().execute()
            return result.get('items', [])
        except Exception as e:
            logger.error(f"Failed to list task lists: {e}")
            return []

    def create_task_list(self, title: str) -> Optional[Dict[str, Any]]:
        """Create a new task list"""
        try:
            service = self._get_tasks_service()
            task_list_body = {
                'title': title
            }
            
            result = service.tasklists().insert(body=task_list_body).execute()
            logger.info(f"Created task list: {title}")
            return result
        except Exception as e:
            logger.error(f"Failed to create task list: {e}")
            return None

    def get_task_list(self, list_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific task list"""
        try:
            service = self._get_tasks_service()
            result = service.tasklists().get(tasklist=list_id).execute()
            return result
        except Exception as e:
            logger.error(f"Failed to get task list {list_id}: {e}")
            return None

    def list_tasks(self, list_id: str = "@default", show_completed: bool = False, 
                   show_deleted: bool = False, show_hidden: bool = False) -> List[Dict[str, Any]]:
        """List tasks in a task list"""
        try:
            service = self._get_tasks_service()
            result = service.tasks().list(
                tasklist=list_id,
                showCompleted=show_completed,
                showDeleted=show_deleted,
                showHidden=show_hidden
            ).execute()
            return result.get('items', [])
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            return []

    def create_task(self, title: str, notes: Optional[str] = None, 
                   due: Optional[datetime] = None, parent: Optional[str] = None,
                   list_id: str = "@default") -> Optional[Dict[str, Any]]:
        """Create a new task"""
        try:
            service = self._get_tasks_service()
            
            task_body = {
                'title': title
            }
            
            if notes:
                task_body['notes'] = notes
            
            if due:
                # Google Tasks expects RFC 3339 timestamp
                task_body['due'] = due.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            if parent:
                task_body['parent'] = parent
            
            result = service.tasks().insert(
                tasklist=list_id, 
                body=task_body,
                parent=parent
            ).execute()
            
            logger.info(f"Created task: {title}")
            return result
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return None

    def get_task(self, task_id: str, list_id: str = "@default") -> Optional[Dict[str, Any]]:
        """Get a specific task"""
        try:
            service = self._get_tasks_service()
            result = service.tasks().get(tasklist=list_id, task=task_id).execute()
            return result
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            return None

    def update_task(self, task_id: str, list_id: str = "@default", 
                   title: Optional[str] = None, notes: Optional[str] = None,
                   due: Optional[datetime] = None, status: Optional[TaskStatus] = None,
                   completed: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """Update an existing task"""
        try:
            service = self._get_tasks_service()
            
            # Get current task
            current_task = service.tasks().get(tasklist=list_id, task=task_id).execute()
            
            # Update fields
            if title is not None:
                current_task['title'] = title
            if notes is not None:
                current_task['notes'] = notes
            if due is not None:
                current_task['due'] = due.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            if status is not None:
                current_task['status'] = status.value
            if completed is not None:
                current_task['completed'] = completed.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            result = service.tasks().update(
                tasklist=list_id, 
                task=task_id,
                body=current_task
            ).execute()
            
            logger.info(f"Updated task: {task_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            return None

    def delete_task(self, task_id: str, list_id: str = "@default") -> bool:
        """Delete a task"""
        try:
            service = self._get_tasks_service()
            service.tasks().delete(tasklist=list_id, task=task_id).execute()
            logger.info(f"Deleted task: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            return False

    def mark_task_completed(self, task_id: str, list_id: str = "@default") -> Optional[Dict[str, Any]]:
        """Mark a task as completed"""
        return self.update_task(
            task_id=task_id,
            list_id=list_id,
            status=TaskStatus.COMPLETED,
            completed=datetime.now()
        )

    def clear_completed_tasks(self, list_id: str = "@default") -> bool:
        """Clear all completed tasks from a list"""
        try:
            service = self._get_tasks_service()
            service.tasks().clear(tasklist=list_id).execute()
            logger.info(f"Cleared completed tasks from list: {list_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear completed tasks: {e}")
            return False