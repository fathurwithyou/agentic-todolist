"""
Calendar domain models.
Timeline parsing and calendar event entities.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum


class EventType(Enum):
    """Types of calendar items"""

    EVENT = "event"
    TASK = "task"
    APPOINTMENT = "appointment"


@dataclass
class ParsedEvent:
    """Event parsed from timeline text"""

    title: str
    description: str
    start_date: str  # ISO format date
    end_date: str  # ISO format date
    start_time: Optional[str] = None  # ISO format time
    end_time: Optional[str] = None  # ISO format time
    attendees: List[str] = None
    location: Optional[str] = None
    all_day: bool = True

    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []


@dataclass
class CalendarEvent:
    """Calendar event entity"""

    event_id: str
    user_id: str
    title: str
    description: str
    start_datetime: datetime
    end_datetime: datetime
    attendees: List[str]
    location: Optional[str] = None
    all_day: bool = False
    event_type: EventType = EventType.EVENT
    google_event_id: Optional[str] = None
    html_link: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class TimelineParseRequest:
    """Request to parse timeline text"""

    user_id: str
    timeline_text: str
    flexible: bool = True
    provider: Optional[str] = None
    model: Optional[str] = None
    target_calendar_id: str = "primary"


@dataclass
class TimelineParseResult:
    """Result of timeline parsing"""

    events: List[ParsedEvent]
    provider_used: str
    model_used: str
    total_events: int
    processing_time_ms: int

    def __post_init__(self):
        self.total_events = len(self.events)
