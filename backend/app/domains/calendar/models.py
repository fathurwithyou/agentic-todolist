"""
Calendar domain models.
Timeline parsing and calendar event entities.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class EventType(Enum):
    """Types of calendar items"""

    EVENT = "event"
    TASK = "task"
    APPOINTMENT = "appointment"


class EventStatus(Enum):
    """Event status values"""
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"


class EventVisibility(Enum):
    """Event visibility values"""
    DEFAULT = "default"
    PUBLIC = "public"
    PRIVATE = "private"


class EventTransparency(Enum):
    """Event transparency values"""
    OPAQUE = "opaque"
    TRANSPARENT = "transparent"


class AttendeeResponseStatus(Enum):
    """Attendee response status values"""
    NEEDS_ACTION = "needsAction"
    DECLINED = "declined"
    TENTATIVE = "tentative"
    ACCEPTED = "accepted"


@dataclass
class EventDateTime:
    """Event start/end datetime"""
    date: Optional[str] = None  # For all-day events (YYYY-MM-DD)
    dateTime: Optional[str] = None  # For timed events (ISO 8601)
    timeZone: Optional[str] = None


@dataclass
class Person:
    """Person (creator/organizer)"""
    id: Optional[str] = None
    email: Optional[str] = None
    displayName: Optional[str] = None
    self: Optional[bool] = None


@dataclass
class Attendee:
    """Event attendee"""
    id: Optional[str] = None
    email: Optional[str] = None
    displayName: Optional[str] = None
    organizer: Optional[bool] = None
    self: Optional[bool] = None
    resource: Optional[bool] = None
    optional: Optional[bool] = None
    responseStatus: Optional[AttendeeResponseStatus] = None
    comment: Optional[str] = None
    additionalGuests: Optional[int] = None


@dataclass
class ReminderOverride:
    """Custom reminder override"""
    method: str  # "email" or "popup"
    minutes: int  # Minutes before event


@dataclass
class Reminders:
    """Event reminders"""
    useDefault: bool = True
    overrides: List[ReminderOverride] = field(default_factory=list)


@dataclass
class ConferenceEntryPoint:
    """Conference entry point"""
    entryPointType: str  # "video", "phone", "sip", "more"
    uri: Optional[str] = None
    label: Optional[str] = None
    pin: Optional[str] = None
    accessCode: Optional[str] = None
    meetingCode: Optional[str] = None
    passcode: Optional[str] = None
    password: Optional[str] = None


@dataclass
class ConferenceSolution:
    """Conference solution details"""
    key: Dict[str, str]  # {"type": "hangoutsMeet"}
    name: Optional[str] = None
    iconUri: Optional[str] = None


@dataclass
class ConferenceData:
    """Conference data"""
    createRequest: Optional[Dict[str, Any]] = None
    entryPoints: List[ConferenceEntryPoint] = field(default_factory=list)
    conferenceSolution: Optional[ConferenceSolution] = None
    conferenceId: Optional[str] = None
    signature: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class Attachment:
    """Event attachment"""
    fileUrl: str
    title: Optional[str] = None
    mimeType: Optional[str] = None
    iconLink: Optional[str] = None
    fileId: Optional[str] = None


@dataclass
class ParsedEvent:
    """Event parsed from timeline text"""

    title: str
    description: str
    start_date: str  # ISO format date
    end_date: str  # ISO format date
    start_time: Optional[str] = None  # ISO format time
    end_time: Optional[str] = None  # ISO format time
    attendees: List[str] = field(default_factory=list)
    location: Optional[str] = None
    all_day: bool = True
    
    # Additional Google Calendar fields
    status: EventStatus = EventStatus.CONFIRMED
    visibility: EventVisibility = EventVisibility.DEFAULT
    transparency: EventTransparency = EventTransparency.OPAQUE
    colorId: Optional[str] = None
    recurrence: List[str] = field(default_factory=list)
    reminders: Optional[Reminders] = None
    conferenceData: Optional[ConferenceData] = None
    attachments: List[Attachment] = field(default_factory=list)
    creator: Optional[Person] = None
    organizer: Optional[Person] = None
    sequence: int = 0
    
    def __post_init__(self):
        if self.reminders is None:
            self.reminders = Reminders()


@dataclass
class CalendarEvent:
    """Calendar event entity - full Google Calendar API representation"""

    # Basic identification
    event_id: str
    user_id: str
    title: str  # summary in Google API
    description: str
    
    # Temporal properties
    start: EventDateTime
    end: EventDateTime
    all_day: bool = False
    
    # Participants
    attendees: List[Attendee] = field(default_factory=list)
    creator: Optional[Person] = None
    organizer: Optional[Person] = None
    
    # Location and conferencing
    location: Optional[str] = None
    conferenceData: Optional[ConferenceData] = None
    
    # Event metadata
    status: EventStatus = EventStatus.CONFIRMED
    visibility: EventVisibility = EventVisibility.DEFAULT
    transparency: EventTransparency = EventTransparency.OPAQUE
    colorId: Optional[str] = None
    event_type: EventType = EventType.EVENT
    
    # Recurrence
    recurrence: List[str] = field(default_factory=list)
    recurringEventId: Optional[str] = None
    originalStartTime: Optional[EventDateTime] = None
    
    # Notifications
    reminders: Optional[Reminders] = None
    
    # Attachments
    attachments: List[Attachment] = field(default_factory=list)
    
    # Google Calendar specific
    google_event_id: Optional[str] = None  # id in Google API
    etag: Optional[str] = None
    html_link: Optional[str] = None
    iCalUID: Optional[str] = None
    sequence: int = 0
    
    # System metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.reminders is None:
            self.reminders = Reminders()


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
