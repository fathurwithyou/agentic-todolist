"""
Event-related data schemas.
Clean separation between data models and business logic.
"""

from typing import List, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field


@dataclass
class ParsedEvent:
    """Domain model for a parsed timeline event"""

    title: str
    start_date: str  # ISO format YYYY-MM-DD
    end_date: str  # ISO format YYYY-MM-DD
    description: str
    attendees: List[str]


@dataclass
class CreatedEvent:
    """Domain model for a successfully created calendar event"""

    id: str
    summary: str
    start_date: str
    end_date: str
    html_link: str


class TimelineRequest(BaseModel):
    """API request schema for timeline parsing"""

    timeline_text: str = Field(
        ...,
        description="Timeline text or flexible prompt to parse and convert to calendar events",
        example="Timeline Gemastik\n\n1 Juli–10 Agustus: Masa Submisi Proposal\n11 Agustus–2 September: Penjurian\n8 September: Pengumuman Finalis\n27–30 Oktober: Babak Final\n\nInvite: Fathur, Bimo, Guntara",
    )
    flexible: bool = Field(
        True,
        description="Whether to use flexible prompt handling for non-standard timeline formats",
    )
    llm_provider: Optional[str] = Field(
        None,
        description="LLM provider to use: 'gemini' or 'openai'. If not specified, uses default from config",
    )
    llm_model: Optional[str] = Field(
        None,
        description="Specific model name to use. If not specified, uses default for the provider",
    )
    api_key: Optional[str] = Field(
        None,
        description="API key for the LLM provider. If not specified, uses environment variable",
    )
    oauth_token: Optional[str] = Field(
        None,
        description="OAuth access token for the LLM provider (preferred over API key)",
    )
    user_id: Optional[str] = Field(
        None,
        description="User identifier for logging and audit purposes",
    )


class CreatedEventResponse(BaseModel):
    """API response schema for created events"""

    id: str
    summary: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    html_link: Optional[str] = None


class TimelineResponse(BaseModel):
    """API response schema for timeline processing"""

    created_events: List[CreatedEventResponse]
    total_events: int
    success_count: int


class PreviewEventResponse(BaseModel):
    """API response schema for event preview"""

    title: str
    start_date: str
    end_date: str
    description: str
    attendees: List[str]


class TimelinePreviewResponse(BaseModel):
    """API response schema for timeline preview"""

    parsed_events: List[PreviewEventResponse]
    total_events: int
    used_provider: Optional[str] = None
    used_model: Optional[str] = None


class CreateEventsRequest(BaseModel):
    """API request schema for creating events from parsed data"""

    events: List[PreviewEventResponse] = Field(
        ..., description="List of events to create in calendar"
    )


class CreateItemRequest(BaseModel):
    """API request schema for creating individual events/tasks/appointments"""

    title: str = Field(..., description="Title of the event/task/appointment")
    description: Optional[str] = Field(None, description="Optional description")
    start_date: str = Field(..., description="Start date in ISO format YYYY-MM-DD")
    end_date: str = Field(..., description="End date in ISO format YYYY-MM-DD")
    start_time: Optional[str] = Field(
        None, description="Start time in HH:MM format (24-hour)"
    )
    end_time: Optional[str] = Field(
        None, description="End time in HH:MM format (24-hour)"
    )
    attendees: Optional[List[str]] = Field(
        default_factory=list, description="List of attendee names or emails"
    )
    item_type: str = Field(
        ..., description="Type of item: 'event', 'task', or 'appointment'"
    )
    all_day: bool = Field(default=True, description="Whether this is an all-day event")


class CreateItemResponse(BaseModel):
    """API response schema for created individual items"""

    id: str
    summary: str
    start_date: str
    end_date: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    html_link: Optional[str] = None
    item_type: str
