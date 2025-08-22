"""
Timeline API endpoints.
Handles timeline-specific operations and provider management.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ..domains.llm.service import LLMService
from ..domains.llm.encryption import APIKeyEncryption
from ..domains.calendar.service import CalendarService
from ..domains.calendar.models import TimelineParseRequest
from ..infrastructure.llm_repository import FileLLMRepository
from ..services.user_calendar_service import create_user_calendar_service
from .auth import get_current_user

logger = logging.getLogger(__name__)

# Initialize dependencies
llm_repository = FileLLMRepository()
encryption = APIKeyEncryption()
llm_service = LLMService(llm_repository, encryption)


# For calendar service (reusing the same pattern as calendar.py)
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

router = APIRouter(prefix="/timeline", tags=["timeline"])


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


class CreateEventsRequest(BaseModel):
    """Request to create multiple events from preview"""

    events: List[ParsedEventResponse]


@router.get("/providers")
async def get_timeline_providers(current_user=Depends(get_current_user)):
    """Get available LLM providers for timeline parsing"""
    try:
        providers = llm_service.get_available_providers()
        return {
            "available_providers": [p["name"] for p in providers],
            "provider_models": {p["name"]: p["models"] for p in providers},
        }
    except Exception as e:
        logger.error(f"Failed to get timeline providers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get providers")


@router.post("/preview", response_model=TimelinePreviewResponse)
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


@router.post("/create-events")
async def create_events_from_timeline(
    request: CreateEventsRequest, current_user=Depends(get_current_user)
):
    """Create calendar events from previewed timeline data directly in Google Calendar"""
    try:
        # Get user's calendar service
        user_calendar_service = create_user_calendar_service(current_user.user)

        created_events = []
        failed_events = []

        # Create each event in Google Calendar
        for event in request.events:
            try:
                # Parse datetime if provided, otherwise use date
                start_datetime = None
                end_datetime = None

                if event.start_time and event.end_time:
                    from datetime import datetime

                    start_datetime = datetime.fromisoformat(
                        f"{event.start_date}T{event.start_time}"
                    )
                    end_datetime = datetime.fromisoformat(
                        f"{event.end_date}T{event.end_time}"
                    )

                created_event = user_calendar_service.create_event(
                    title=event.title,
                    description=event.description,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    start_date=event.start_date if not start_datetime else None,
                    end_date=event.end_date if not end_datetime else None,
                    attendees=event.attendees,
                    location=event.location,
                )

                if created_event:
                    created_events.append(created_event)
                    logger.info(f"Created Google Calendar event: {event.title}")
                else:
                    failed_events.append(event.title)
                    logger.error(
                        f"Failed to create Google Calendar event: {event.title}"
                    )

            except Exception as e:
                failed_events.append(event.title)
                logger.error(f"Error creating event '{event.title}': {e}")

        return {
            "success": len(created_events) > 0,
            "total_events": len(request.events),
            "success_count": len(created_events),
            "failed_count": len(failed_events),
            "created_events": [
                {
                    "id": event["id"],
                    "summary": event["summary"],
                    "start": event["start"],
                    "end": event["end"],
                    "html_link": event["html_link"],
                    "location": event.get("location", ""),
                    "description": event.get("description", ""),
                }
                for event in created_events
            ],
            "failed_events": failed_events,
        }

    except Exception as e:
        logger.error(f"Timeline event creation failed: {e}")
        raise HTTPException(status_code=500, detail="Timeline event creation failed")
