"""
Timeline API endpoints.
Handles timeline-specific operations and provider management.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ..domains.calendar.models import TimelineParseRequest
from ..domains.calendar.service import CalendarService
from ..domains.calendar.user_service import create_user_calendar_service
from ..domains.llm.service import LLMService
from ..domains.llm.encryption import APIKeyEncryption
from ..infrastructure.llm_repository import FileLLMRepository
from .auth import get_current_user

logger = logging.getLogger(__name__)

# Initialize LLM service
llm_repository = FileLLMRepository()
encryption = APIKeyEncryption()
llm_service = LLMService(llm_repository, encryption)

router = APIRouter(prefix="/timeline", tags=["timeline"])


class TimelineRequest(BaseModel):
    """Request to parse timeline text"""

    timeline_text: str
    flexible: bool = True
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    target_calendar_id: str = "primary"


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

    # Additional Google Calendar fields
    status: str = "confirmed"
    visibility: str = "default"
    transparency: str = "opaque"
    colorId: Optional[str] = None
    recurrence: List[str] = []
    reminders: Optional[dict] = None
    conferenceData: Optional[dict] = None
    sequence: int = 0


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
    target_calendar_id: str = "primary"


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
        
        provider_type = None
        if request.llm_provider:
            try:
                from ..domains.llm.models import ProviderType
                provider_type = ProviderType(request.llm_provider.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported provider: {request.llm_provider}"
                )
        else:
            provider_type = ProviderType.GEMINI  # Default
        
        api_key = llm_service.get_api_key(current_user.user.user_id, provider_type)
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail=f"No API key found for {provider_type.value}. Please save your API key first."
            )
        
        # Parse timeline using LLM provider directly
        from ..providers.factory import LLMFactory
        provider = LLMFactory.create_provider(
            provider_name=provider_type.value,
            api_key=api_key,
            model_name=request.llm_model
        )
        
        if not provider:
            raise HTTPException(
                status_code=500, 
                detail="Failed to create LLM provider"
            )
        
        await provider.initialize()
        if not provider.is_available():
            raise HTTPException(
                status_code=500,
                detail="LLM provider not available"
            )
        
        # Get user's system prompt
        from ..infrastructure.auth_repository import FileAuthRepository
        auth_repository = FileAuthRepository()
        user = auth_repository.get_user(current_user.user.user_id)
        system_prompt = user.system_prompt if user else None
        
        # Parse timeline
        import time
        start_time = time.time()
        events = await provider.parse_timeline(request.timeline_text, system_prompt)
        processing_time_ms = int((time.time() - start_time) * 1000)
        
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
                status=event.status.value,
                visibility=event.visibility.value,
                transparency=event.transparency.value,
                colorId=event.colorId,
                recurrence=event.recurrence,
                reminders={"useDefault": event.reminders.useDefault}
                if event.reminders
                else None,
                conferenceData=None,  # Simplified for now
                sequence=event.sequence,
            )
            for event in events
        ]

        return TimelinePreviewResponse(
            parsed_events=parsed_events,
            total_events=len(events),
            used_provider=provider_type.value,
            used_model=request.llm_model or provider.model_name,
            processing_time_ms=processing_time_ms,
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
        logger.info(
            f"🎯 Creating events (timeline.py) - User: {current_user.user.user_id}, Calendar: '{request.target_calendar_id}', Events: {len(request.events)}"
        )

        # Get user's calendar service
        user_calendar_service = create_user_calendar_service(current_user.user)

        created_events = []
        failed_events = []

        # Create each event in Google Calendar
        for event in request.events:
            try:
                # Convert ParsedEventResponse back to ParsedEvent
                from ..domains.calendar.models import (
                    ParsedEvent,
                    EventStatus,
                    EventVisibility,
                    EventTransparency,
                    Reminders,
                )

                # Parse status
                status = EventStatus.CONFIRMED
                if event.status == "tentative":
                    status = EventStatus.TENTATIVE
                elif event.status == "cancelled":
                    status = EventStatus.CANCELLED

                # Parse visibility
                visibility = EventVisibility.DEFAULT
                if event.visibility == "public":
                    visibility = EventVisibility.PUBLIC
                elif event.visibility == "private":
                    visibility = EventVisibility.PRIVATE

                # Parse transparency
                transparency = EventTransparency.OPAQUE
                if event.transparency == "transparent":
                    transparency = EventTransparency.TRANSPARENT

                # Create ParsedEvent object
                parsed_event = ParsedEvent(
                    title=event.title,
                    description=event.description,
                    start_date=event.start_date,
                    end_date=event.end_date,
                    start_time=event.start_time,
                    end_time=event.end_time,
                    attendees=event.attendees,
                    location=event.location,
                    all_day=event.all_day,
                    status=status,
                    visibility=visibility,
                    transparency=transparency,
                    colorId=event.colorId,
                    recurrence=event.recurrence,
                    reminders=Reminders(useDefault=True)
                    if not event.reminders
                    else Reminders(useDefault=event.reminders.get("useDefault", True)),
                    sequence=event.sequence,
                )

                created_event = user_calendar_service.create_event_from_parsed(
                    parsed_event=parsed_event,
                    calendar_id=request.target_calendar_id,
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
                    "status": event.get("status", ""),
                    "recurrence": event.get("recurrence", []),
                    "reminders": event.get("reminders", {}),
                    "conferenceData": event.get("conferenceData", {}),
                    # Add parsed date/time for frontend display
                    "start_date": event["start"].get("date")
                    or event["start"].get("dateTime", "").split("T")[0]
                    if event.get("start")
                    else "",
                    "end_date": event["end"].get("date")
                    or event["end"].get("dateTime", "").split("T")[0]
                    if event.get("end")
                    else "",
                    "start_time": event["start"].get("dateTime", "").split("T")[1][:5]
                    if event.get("start", {}).get("dateTime")
                    else None,
                    "end_time": event["end"].get("dateTime", "").split("T")[1][:5]
                    if event.get("end", {}).get("dateTime")
                    else None,
                    "all_day": "date" in event.get("start", {}),
                }
                for event in created_events
            ],
            "failed_events": failed_events,
        }

    except Exception as e:
        logger.error(f"Timeline event creation failed: {e}")
        raise HTTPException(status_code=500, detail="Timeline event creation failed")
