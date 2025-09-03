"""
Task domain models.
Google Tasks API integration and task management entities.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class TaskStatus(Enum):
    """Task status values"""
    NEEDS_ACTION = "needsAction"
    COMPLETED = "completed"


class TaskPriority(Enum):
    """Task priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TaskLink:
    """Task link attachment"""
    type: str
    description: Optional[str] = None
    link: Optional[str] = None


@dataclass
class DriveResourceInfo:
    """Drive resource information"""
    drive_file_id: str
    resource_key: Optional[str] = None


@dataclass
class SpaceInfo:
    """Google Workspace space information"""
    space: str


@dataclass
class AssignmentInfo:
    """Task assignment information"""
    link_to_task: Optional[str] = None
    surface_type: Optional[str] = None
    drive_resource_info: Optional[DriveResourceInfo] = None
    space_info: Optional[SpaceInfo] = None


@dataclass
class GoogleTask:
    """Google Task entity - full Google Tasks API representation"""
    
    # Basic identification
    task_id: str
    user_id: str
    title: str
    notes: Optional[str] = None
    
    # Task properties
    status: TaskStatus = TaskStatus.NEEDS_ACTION
    due: Optional[datetime] = None
    completed: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    
    # Hierarchy
    parent: Optional[str] = None
    position: Optional[str] = None
    
    # Google Tasks specific
    google_task_id: Optional[str] = None
    etag: Optional[str] = None
    kind: str = "tasks#task"
    self_link: Optional[str] = None
    web_view_link: Optional[str] = None
    deleted: bool = False
    hidden: bool = False
    
    # Links and assignments
    links: List[TaskLink] = field(default_factory=list)
    assignment_info: Optional[AssignmentInfo] = None
    
    # System metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    google_updated: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class GoogleTaskList:
    """Google Task List entity"""
    
    # Basic identification
    list_id: str
    user_id: str
    title: str
    
    # Google TaskList specific
    google_list_id: Optional[str] = None
    etag: Optional[str] = None
    kind: str = "tasks#taskList"
    self_link: Optional[str] = None
    
    # System metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    google_updated: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class ParsedTask:
    """Task parsed from timeline text"""
    
    title: str
    notes: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[str] = None  # ISO format date
    due_time: Optional[str] = None  # ISO format time
    completed: bool = False
    parent_task: Optional[str] = None