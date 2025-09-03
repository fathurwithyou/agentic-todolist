"""
Task repository.
Handles task data persistence.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from pathlib import Path

from .models import GoogleTask, GoogleTaskList

logger = logging.getLogger(__name__)


class TaskRepository:
    """File-based task repository"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.tasks_dir = self.data_dir / "tasks"
        self.task_lists_dir = self.data_dir / "task_lists"
        
        # Ensure directories exist
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.task_lists_dir.mkdir(parents=True, exist_ok=True)

    def save_task(self, task: GoogleTask) -> GoogleTask:
        """Save task to file system"""
        task_file = self.tasks_dir / f"{task.task_id}.json"
        task.updated_at = datetime.now()
        
        with task_file.open("w") as f:
            json.dump(self._task_to_dict(task), f, indent=2, default=str)
        
        logger.info(f"Saved task {task.task_id}")
        return task

    def get_task(self, task_id: str) -> Optional[GoogleTask]:
        """Get task by ID"""
        task_file = self.tasks_dir / f"{task_id}.json"
        
        if not task_file.exists():
            return None
        
        try:
            with task_file.open("r") as f:
                task_data = json.load(f)
            return self._dict_to_task(task_data)
        except Exception as e:
            logger.error(f"Failed to load task {task_id}: {e}")
            return None

    def get_user_tasks(self, user_id: str, list_id: Optional[str] = None) -> List[GoogleTask]:
        """Get all tasks for a user, optionally filtered by list"""
        tasks = []
        
        for task_file in self.tasks_dir.glob("*.json"):
            try:
                with task_file.open("r") as f:
                    task_data = json.load(f)
                
                task = self._dict_to_task(task_data)
                if task.user_id == user_id:
                    if list_id is None or task.parent == list_id:
                        tasks.append(task)
                        
            except Exception as e:
                logger.error(f"Failed to load task from {task_file}: {e}")
        
        # Sort by creation time
        tasks.sort(key=lambda x: x.created_at or datetime.min)
        return tasks

    def delete_task(self, task_id: str) -> bool:
        """Delete task"""
        task_file = self.tasks_dir / f"{task_id}.json"
        
        if task_file.exists():
            task_file.unlink()
            logger.info(f"Deleted task {task_id}")
            return True
        return False

    def update_task(self, task: GoogleTask) -> GoogleTask:
        """Update existing task"""
        return self.save_task(task)

    def save_task_list(self, task_list: GoogleTaskList) -> GoogleTaskList:
        """Save task list to file system"""
        list_file = self.task_lists_dir / f"{task_list.list_id}.json"
        task_list.updated_at = datetime.now()
        
        with list_file.open("w") as f:
            json.dump(self._task_list_to_dict(task_list), f, indent=2, default=str)
        
        logger.info(f"Saved task list {task_list.list_id}")
        return task_list

    def get_task_list(self, list_id: str) -> Optional[GoogleTaskList]:
        """Get task list by ID"""
        list_file = self.task_lists_dir / f"{list_id}.json"
        
        if not list_file.exists():
            return None
        
        try:
            with list_file.open("r") as f:
                list_data = json.load(f)
            return self._dict_to_task_list(list_data)
        except Exception as e:
            logger.error(f"Failed to load task list {list_id}: {e}")
            return None

    def get_user_task_lists(self, user_id: str) -> List[GoogleTaskList]:
        """Get all task lists for a user"""
        task_lists = []
        
        for list_file in self.task_lists_dir.glob("*.json"):
            try:
                with list_file.open("r") as f:
                    list_data = json.load(f)
                
                task_list = self._dict_to_task_list(list_data)
                if task_list.user_id == user_id:
                    task_lists.append(task_list)
                        
            except Exception as e:
                logger.error(f"Failed to load task list from {list_file}: {e}")
        
        task_lists.sort(key=lambda x: x.created_at or datetime.min)
        return task_lists

    def delete_task_list(self, list_id: str) -> bool:
        """Delete task list"""
        list_file = self.task_lists_dir / f"{list_id}.json"
        
        if list_file.exists():
            list_file.unlink()
            logger.info(f"Deleted task list {list_id}")
            return True
        return False

    def _task_to_dict(self, task: GoogleTask) -> Dict[str, Any]:
        """Convert task to dictionary for JSON serialization"""
        return {
            "task_id": task.task_id,
            "user_id": task.user_id,
            "title": task.title,
            "notes": task.notes,
            "status": task.status.value if task.status else None,
            "due": task.due.isoformat() if task.due else None,
            "completed": task.completed.isoformat() if task.completed else None,
            "priority": task.priority.value if task.priority else None,
            "parent": task.parent,
            "position": task.position,
            "google_task_id": task.google_task_id,
            "etag": task.etag,
            "kind": task.kind,
            "self_link": task.self_link,
            "web_view_link": task.web_view_link,
            "deleted": task.deleted,
            "hidden": task.hidden,
            "links": [{"type": link.type, "description": link.description, "link": link.link} for link in task.links],
            "assignment_info": task.assignment_info.__dict__ if task.assignment_info else None,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            "google_updated": task.google_updated.isoformat() if task.google_updated else None,
        }

    def _dict_to_task(self, data: Dict[str, Any]) -> GoogleTask:
        """Convert dictionary to task object"""
        from .models import TaskStatus, TaskPriority, TaskLink, AssignmentInfo
        
        task = GoogleTask(
            task_id=data["task_id"],
            user_id=data["user_id"],
            title=data["title"],
            notes=data.get("notes"),
            status=TaskStatus(data["status"]) if data.get("status") else TaskStatus.NEEDS_ACTION,
            due=datetime.fromisoformat(data["due"]) if data.get("due") else None,
            completed=datetime.fromisoformat(data["completed"]) if data.get("completed") else None,
            priority=TaskPriority(data["priority"]) if data.get("priority") else None,
            parent=data.get("parent"),
            position=data.get("position"),
            google_task_id=data.get("google_task_id"),
            etag=data.get("etag"),
            kind=data.get("kind", "tasks#task"),
            self_link=data.get("self_link"),
            web_view_link=data.get("web_view_link"),
            deleted=data.get("deleted", False),
            hidden=data.get("hidden", False),
            links=[TaskLink(**link) for link in data.get("links", [])],
            assignment_info=AssignmentInfo(**data["assignment_info"]) if data.get("assignment_info") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            google_updated=datetime.fromisoformat(data["google_updated"]) if data.get("google_updated") else None,
        )
        return task

    def _task_list_to_dict(self, task_list: GoogleTaskList) -> Dict[str, Any]:
        """Convert task list to dictionary for JSON serialization"""
        return {
            "list_id": task_list.list_id,
            "user_id": task_list.user_id,
            "title": task_list.title,
            "google_list_id": task_list.google_list_id,
            "etag": task_list.etag,
            "kind": task_list.kind,
            "self_link": task_list.self_link,
            "created_at": task_list.created_at.isoformat() if task_list.created_at else None,
            "updated_at": task_list.updated_at.isoformat() if task_list.updated_at else None,
            "google_updated": task_list.google_updated.isoformat() if task_list.google_updated else None,
        }

    def _dict_to_task_list(self, data: Dict[str, Any]) -> GoogleTaskList:
        """Convert dictionary to task list object"""
        task_list = GoogleTaskList(
            list_id=data["list_id"],
            user_id=data["user_id"],
            title=data["title"],
            google_list_id=data.get("google_list_id"),
            etag=data.get("etag"),
            kind=data.get("kind", "tasks#taskList"),
            self_link=data.get("self_link"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            google_updated=datetime.fromisoformat(data["google_updated"]) if data.get("google_updated") else None,
        )
        return task_list