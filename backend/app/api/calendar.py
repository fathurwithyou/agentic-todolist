"""
Clean calendar API endpoints.
Uses domain services for timeline and calendar operations.
"""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from ..services.user_calendar_service import create_user_calendar_service
from .auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/calendar", tags=["calendar"])


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


@router.get("/google/calendars/writable", response_model=List[CalendarListResponse])
async def list_writable_calendars(current_user=Depends(get_current_user)):
    """List only the user's writable Google Calendars (for event creation)"""
    try:
        user_calendar_service = create_user_calendar_service(current_user.user)
        calendars = user_calendar_service.list_writable_calendars()

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
        logger.error(f"Failed to list writable calendars: {e}")
        raise HTTPException(status_code=500, detail="Failed to list writable calendars")


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
