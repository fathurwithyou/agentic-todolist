"""
Clean calendar API endpoints.
Uses domain services for timeline and calendar operations.
"""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from ..domains.calendar.service import CalendarService
from ..domains.calendar.models import TimelineParseRequest, ParsedEvent
from ..domains.llm.service import LLMService
from ..domains.llm.encryption import APIKeyEncryption
from ..infrastructure.llm_repository import FileLLMRepository
from ..services.user_calendar_service import create_user_calendar_service
from .auth import get_current_user

logger = logging.getLogger(__name__)

# Initialize dependencies
llm_repository = FileLLMRepository()
encryption = APIKeyEncryption()
llm_service = LLMService(llm_repository, encryption)


# For now, we'll use a simple in-memory calendar repository
# In a real app, this would be a proper database implementation
class InMemoryCalendarRepository:
    def __init__(self):
        self.events = []

    def save_event(self, event):
        self.events.append(event)
        return event

    def get_user_events(self, user_id):
        return [e for e in self.events if e.user_id == user_id]


calendar_repository = InMemoryCalendarRepository()
calendar_service = CalendarService(calendar_repository, llm_service)

router = APIRouter(prefix="/calendar", tags=["calendar"])


class TimelineRequest(BaseModel):
    """Request to parse timeline text"""

    timeline_text: str
    flexible: bool = True
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None


class ParsedEventResponse(BaseModel):
    """Parsed event response"""

    title: str
    description: str
    start_date: str
    end_date: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    attendees: List[str] = []
    location: Optional[str] = None
    all_day: bool = True


class TimelinePreviewResponse(BaseModel):
    """Timeline preview response"""

    parsed_events: List[ParsedEventResponse]
    total_events: int
    used_provider: str
    used_model: str
    processing_time_ms: int


class CreateEventRequest(BaseModel):
    """Request to create a single calendar event"""

    title: str
    description: str = ""
    start_date: str
    end_date: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    attendees: List[str] = []
    location: Optional[str] = None
    all_day: bool = True
    item_type: str = "event"


class CreateEventsRequest(BaseModel):
    """Request to create multiple events from preview"""

    events: List[ParsedEventResponse]


class GoogleEventResponse(BaseModel):
    """Google Calendar event response"""

    id: str
    summary: str
    description: str = ""
    start: dict
    end: dict
    location: str = ""
    attendees: List[dict] = []
    html_link: str = ""
    created: str = ""
    updated: str = ""
    status: str = ""


class CreateGoogleEventRequest(BaseModel):
    """Request to create an event directly in Google Calendar"""

    title: str
    description: str = ""
    start_datetime: Optional[str] = None  # ISO format datetime
    end_datetime: Optional[str] = None  # ISO format datetime
    start_date: Optional[str] = None  # YYYY-MM-DD format
    end_date: Optional[str] = None  # YYYY-MM-DD format
    attendees: List[str] = []
    location: Optional[str] = None
    calendar_id: str = "primary"


class UpdateGoogleEventRequest(BaseModel):
    """Request to update an existing Google Calendar event"""

    title: Optional[str] = None
    description: Optional[str] = None
    start_datetime: Optional[str] = None  # ISO format datetime
    end_datetime: Optional[str] = None  # ISO format datetime
    start_date: Optional[str] = None  # YYYY-MM-DD format
    end_date: Optional[str] = None  # YYYY-MM-DD format
    attendees: Optional[List[str]] = None
    location: Optional[str] = None


class CalendarListResponse(BaseModel):
    """User's calendar list response"""

    id: str
    summary: str
    description: str = ""
    primary: bool = False
    access_role: str = ""
    color_id: str = ""


@router.post("/timeline/preview", response_model=TimelinePreviewResponse)
async def preview_timeline(
    request: TimelineRequest, current_user=Depends(get_current_user)
):
    """Preview timeline parsing without creating calendar events"""
    try:
        # Create timeline parse request
        parse_request = TimelineParseRequest(
            user_id=current_user.user.user_id,
            timeline_text=request.timeline_text,
            flexible=request.flexible,
            provider=request.llm_provider,
            model=request.llm_model,
        )

        # Parse timeline using domain service
        result = await calendar_service.parse_timeline(parse_request)

        # Convert to response format
        parsed_events = [
            ParsedEventResponse(
                title=event.title,
                description=event.description,
                start_date=event.start_date,
                end_date=event.end_date,
                start_time=event.start_time,
                end_time=event.end_time,
                attendees=event.attendees,
                location=event.location,
                all_day=event.all_day,
            )
            for event in result.events
        ]

        return TimelinePreviewResponse(
            parsed_events=parsed_events,
            total_events=result.total_events,
            used_provider=result.provider_used,
            used_model=result.model_used,
            processing_time_ms=result.processing_time_ms,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Timeline preview failed: {e}")
        raise HTTPException(status_code=500, detail="Timeline preview failed")


@router.post("/timeline/create-events")
async def create_events_from_preview(
    request: CreateEventsRequest, current_user=Depends(get_current_user)
):
    """Create calendar events from previewed timeline data"""
    try:
        # Convert request events to ParsedEvent objects
        parsed_events = [
            ParsedEvent(
                title=event.title,
                description=event.description,
                start_date=event.start_date,
                end_date=event.end_date,
                start_time=event.start_time,
                end_time=event.end_time,
                attendees=event.attendees,
                location=event.location,
                all_day=event.all_day,
            )
            for event in request.events
        ]

        # Create events using domain service
        created_events = calendar_service.create_calendar_events(
            user_id=current_user.user.user_id, parsed_events=parsed_events
        )

        return {
            "success": True,
            "total_events": len(request.events),
            "success_count": len(created_events),
            "created_events": [
                {
                    "id": event.event_id,
                    "summary": event.title,
                    "start_date": event.start_datetime.date().isoformat(),
                    "end_date": event.end_datetime.date().isoformat(),
                    "html_link": event.html_link,
                }
                for event in created_events
            ],
        }

    except Exception as e:
        logger.error(f"Event creation failed: {e}")
        raise HTTPException(status_code=500, detail="Event creation failed")


@router.post("/create")
async def create_single_event(
    request: CreateEventRequest, current_user=Depends(get_current_user)
):
    """Create a single calendar event"""
    try:
        # Convert request to ParsedEvent
        parsed_event = ParsedEvent(
            title=request.title,
            description=request.description,
            start_date=request.start_date,
            end_date=request.end_date,
            start_time=request.start_time,
            end_time=request.end_time,
            attendees=request.attendees,
            location=request.location,
            all_day=request.all_day,
        )

        # Create event using domain service
        created_event = calendar_service.create_calendar_event(
            user_id=current_user.user.user_id, parsed_event=parsed_event
        )

        return {
            "success": True,
            "id": created_event.event_id,
            "summary": created_event.title,
            "item_type": request.item_type,
            "start_date": created_event.start_datetime.date().isoformat(),
            "end_date": created_event.end_datetime.date().isoformat(),
            "start_time": created_event.start_datetime.time().isoformat()
            if not created_event.all_day
            else None,
            "end_time": created_event.end_datetime.time().isoformat()
            if not created_event.all_day
            else None,
            "html_link": created_event.html_link,
        }

    except Exception as e:
        logger.error(f"Single event creation failed: {e}")
        raise HTTPException(status_code=500, detail="Event creation failed")


@router.get("/events")
async def get_user_events(current_user=Depends(get_current_user)):
    """Get all events for the authenticated user"""
    try:
        events = calendar_service.get_user_events(current_user.user.user_id)

        return {
            "events": [
                {
                    "id": event.event_id,
                    "title": event.title,
                    "description": event.description,
                    "start_datetime": event.start_datetime.isoformat(),
                    "end_datetime": event.end_datetime.isoformat(),
                    "all_day": event.all_day,
                    "attendees": event.attendees,
                    "location": event.location,
                }
                for event in events
            ],
            "total_count": len(events),
        }

    except Exception as e:
        logger.error(f"Failed to get user events: {e}")
        raise HTTPException(status_code=500, detail="Failed to get events")


# Google Calendar Integration Endpoints


@router.get("/google/calendars", response_model=List[CalendarListResponse])
async def list_user_calendars(current_user=Depends(get_current_user)):
    """List the user's Google Calendars"""
    try:
        user_calendar_service = create_user_calendar_service(current_user.user)
        calendars = user_calendar_service.list_calendars()

        return [
            CalendarListResponse(
                id=cal["id"],
                summary=cal["summary"],
                description=cal["description"],
                primary=cal["primary"],
                access_role=cal["access_role"],
                color_id=cal["color_id"],
            )
            for cal in calendars
        ]

    except Exception as e:
        logger.error(f"Failed to list user calendars: {e}")
        raise HTTPException(status_code=500, detail="Failed to list calendars")


@router.get("/google/events", response_model=List[GoogleEventResponse])
async def list_google_calendar_events(
    calendar_id: str = Query("primary", description="Calendar ID to list events from"),
    time_min: Optional[str] = Query(None, description="Start time filter (ISO format)"),
    time_max: Optional[str] = Query(None, description="End time filter (ISO format)"),
    max_results: int = Query(100, description="Maximum number of events to return"),
    current_user=Depends(get_current_user),
):
    """List events from the user's Google Calendar"""
    try:
        user_calendar_service = create_user_calendar_service(current_user.user)

        # Parse time filters if provided
        time_min_dt = None
        time_max_dt = None

        if time_min:
            time_min_dt = datetime.fromisoformat(time_min.replace("Z", "+00:00"))
        if time_max:
            time_max_dt = datetime.fromisoformat(time_max.replace("Z", "+00:00"))

        events = user_calendar_service.list_events(
            calendar_id=calendar_id,
            time_min=time_min_dt,
            time_max=time_max_dt,
            max_results=max_results,
        )

        return [
            GoogleEventResponse(
                id=event["id"],
                summary=event["summary"],
                description=event["description"],
                start=event["start"],
                end=event["end"],
                location=event["location"],
                attendees=event["attendees"],
                html_link=event["html_link"],
                created=event["created"],
                updated=event["updated"],
                status=event["status"],
            )
            for event in events
        ]

    except Exception as e:
        logger.error(f"Failed to list Google Calendar events: {e}")
        raise HTTPException(status_code=500, detail="Failed to list events")


@router.post("/google/events", response_model=GoogleEventResponse)
async def create_google_calendar_event(
    request: CreateGoogleEventRequest, current_user=Depends(get_current_user)
):
    """Create an event directly in the user's Google Calendar"""
    try:
        user_calendar_service = create_user_calendar_service(current_user.user)

        # Parse datetime strings if provided
        start_datetime = None
        end_datetime = None

        if request.start_datetime:
            start_datetime = datetime.fromisoformat(
                request.start_datetime.replace("Z", "+00:00")
            )
        if request.end_datetime:
            end_datetime = datetime.fromisoformat(
                request.end_datetime.replace("Z", "+00:00")
            )

        created_event = user_calendar_service.create_event(
            title=request.title,
            description=request.description,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            start_date=request.start_date,
            end_date=request.end_date,
            attendees=request.attendees,
            location=request.location,
            calendar_id=request.calendar_id,
        )

        if not created_event:
            raise HTTPException(status_code=500, detail="Failed to create event")

        return GoogleEventResponse(
            id=created_event["id"],
            summary=created_event["summary"],
            description=created_event["description"],
            start=created_event["start"],
            end=created_event["end"],
            location=created_event["location"],
            attendees=created_event["attendees"],
            html_link=created_event["html_link"],
            status=created_event["status"],
        )

    except Exception as e:
        logger.error(f"Failed to create Google Calendar event: {e}")
        raise HTTPException(status_code=500, detail="Failed to create event")


@router.put("/google/events/{event_id}", response_model=GoogleEventResponse)
async def update_google_calendar_event(
    event_id: str,
    request: UpdateGoogleEventRequest,
    calendar_id: str = Query("primary", description="Calendar ID containing the event"),
    current_user=Depends(get_current_user),
):
    """Update an existing event in the user's Google Calendar"""
    try:
        user_calendar_service = create_user_calendar_service(current_user.user)

        # Parse datetime strings if provided
        start_datetime = None
        end_datetime = None

        if request.start_datetime:
            start_datetime = datetime.fromisoformat(
                request.start_datetime.replace("Z", "+00:00")
            )
        if request.end_datetime:
            end_datetime = datetime.fromisoformat(
                request.end_datetime.replace("Z", "+00:00")
            )

        updated_event = user_calendar_service.update_event(
            event_id=event_id,
            title=request.title,
            description=request.description,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            start_date=request.start_date,
            end_date=request.end_date,
            attendees=request.attendees,
            location=request.location,
            calendar_id=calendar_id,
        )

        if not updated_event:
            raise HTTPException(
                status_code=404, detail="Event not found or update failed"
            )

        return GoogleEventResponse(
            id=updated_event["id"],
            summary=updated_event["summary"],
            description=updated_event["description"],
            start=updated_event["start"],
            end=updated_event["end"],
            location=updated_event["location"],
            attendees=updated_event["attendees"],
            html_link=updated_event["html_link"],
            status=updated_event["status"],
        )

    except Exception as e:
        logger.error(f"Failed to update Google Calendar event: {e}")
        raise HTTPException(status_code=500, detail="Failed to update event")


@router.delete("/google/events/{event_id}")
async def delete_google_calendar_event(
    event_id: str,
    calendar_id: str = Query("primary", description="Calendar ID containing the event"),
    current_user=Depends(get_current_user),
):
    """Delete an event from the user's Google Calendar"""
    try:
        user_calendar_service = create_user_calendar_service(current_user.user)

        success = user_calendar_service.delete_event(
            event_id=event_id, calendar_id=calendar_id
        )

        if not success:
            raise HTTPException(
                status_code=404, detail="Event not found or deletion failed"
            )

        return {"success": True, "message": f"Event {event_id} deleted successfully"}

    except Exception as e:
        logger.error(f"Failed to delete Google Calendar event: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete event")
