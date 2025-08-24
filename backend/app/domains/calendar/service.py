"""
Calendar domain service.
Handles timeline parsing and calendar operations.
"""

import logging
from typing import List, Optional
from datetime import datetime

from .models import (
    ParsedEvent,
    CalendarEvent,
    EventType,
    TimelineParseRequest,
    TimelineParseResult,
)
from .repository import CalendarRepository
from ..llm.service import LLMService
from ..llm.models import ProviderType

logger = logging.getLogger(__name__)


class CalendarService:
    """
    Calendar domain service.
    Handles timeline parsing and calendar event management.
    """

    def __init__(self, repository: CalendarRepository, llm_service: LLMService):
        self.repository = repository
        self.llm_service = llm_service

    async def parse_timeline(
        self, request: TimelineParseRequest
    ) -> TimelineParseResult:
        """Parse timeline text into structured events"""
        start_time = datetime.now()

        # Determine provider and model
        provider = self._determine_provider(request.user_id, request.provider)
        model = request.model or self._get_default_model(provider)

        # Get API key for the provider
        api_key = self.llm_service.get_api_key(request.user_id, provider)
        if not api_key:
            raise ValueError(
                f"No API key found for {provider.value}. "
                f"Please save an API key in the API Keys tab."
            )

        # Parse timeline using LLM
        try:
            events = await self._parse_with_llm(
                request.timeline_text, provider, model, api_key, request.flexible
            )

            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)

            result = TimelineParseResult(
                events=events,
                provider_used=provider.value,
                model_used=model,
                total_events=len(events),
                processing_time_ms=processing_time,
            )

            logger.info(
                f"Parsed {len(events)} events from timeline for user {request.user_id}"
            )
            return result

        except Exception as e:
            logger.error(f"Timeline parsing failed: {e}")
            raise ValueError(f"Failed to parse timeline: {str(e)}")

    def create_calendar_event(
        self,
        user_id: str,
        parsed_event: ParsedEvent,
        target_calendar_id: str = "primary",
    ) -> CalendarEvent:
        """Create a calendar event from parsed event"""
        from ...infrastructure.auth_repository import FileAuthRepository
        from ...services.user_calendar_service import UserCalendarService

        # Get user and create Google Calendar event
        auth_repository = FileAuthRepository()
        user = auth_repository.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        user_calendar_service = UserCalendarService(user, auth_repository)

        # Create event in Google Calendar using the target calendar
        google_event = user_calendar_service.create_event(
            title=parsed_event.title,
            description=parsed_event.description,
            start_date=parsed_event.start_date if parsed_event.all_day else None,
            end_date=parsed_event.end_date if parsed_event.all_day else None,
            start_datetime=self._parse_datetime(
                parsed_event.start_date, parsed_event.start_time
            )
            if not parsed_event.all_day
            else None,
            end_datetime=self._parse_datetime(
                parsed_event.end_date, parsed_event.end_time
            )
            if not parsed_event.all_day
            else None,
            attendees=parsed_event.attendees or [],
            location=parsed_event.location,
            calendar_id=target_calendar_id,
        )

        if not google_event:
            raise ValueError(
                f"Failed to create Google Calendar event: {parsed_event.title}"
            )

        # Convert Google Calendar event to our CalendarEvent model
        event = CalendarEvent(
            event_id=google_event["id"],
            user_id=user_id,
            title=parsed_event.title,
            description=parsed_event.description,
            start_datetime=self._parse_datetime(
                parsed_event.start_date, parsed_event.start_time
            ),
            end_datetime=self._parse_datetime(
                parsed_event.end_date, parsed_event.end_time
            ),
            attendees=parsed_event.attendees or [],
            location=parsed_event.location,
            all_day=parsed_event.all_day,
            event_type=EventType.EVENT,
            google_event_id=google_event["id"],
            html_link=google_event.get("html_link"),
        )

        # Save to repository
        saved_event = self.repository.save_event(event)
        logger.info(
            f"Created Google Calendar event {event.event_id} in calendar '{target_calendar_id}' for user {user_id}"
        )

        return saved_event

    def create_calendar_events(
        self,
        user_id: str,
        parsed_events: List[ParsedEvent],
        target_calendar_id: str = "primary",
    ) -> List[CalendarEvent]:
        """Create multiple calendar events"""
        created_events = []

        for parsed_event in parsed_events:
            try:
                event = self.create_calendar_event(
                    user_id, parsed_event, target_calendar_id
                )
                created_events.append(event)
            except Exception as e:
                logger.error(f"Failed to create event '{parsed_event.title}': {e}")
                # Continue with other events

        logger.info(
            f"Created {len(created_events)}/{len(parsed_events)} events for user {user_id}"
        )
        return created_events

    def get_user_events(self, user_id: str) -> List[CalendarEvent]:
        """Get all events for a user"""
        return self.repository.get_user_events(user_id)

    def _determine_provider(
        self, user_id: str, requested_provider: Optional[str]
    ) -> ProviderType:
        """Determine which provider to use"""
        if requested_provider:
            try:
                provider = ProviderType(requested_provider.lower())
                if self.llm_service.has_api_key(user_id, provider):
                    return provider
                else:
                    logger.warning(
                        f"User {user_id} requested {provider.value} but has no API key"
                    )
            except ValueError:
                logger.warning(f"Invalid provider requested: {requested_provider}")

        # Try providers in order of preference
        for provider in [ProviderType.GEMINI, ProviderType.OPENAI]:
            if self.llm_service.has_api_key(user_id, provider):
                return provider

        raise ValueError(
            "No API keys available. Please save an API key in the API Keys tab."
        )

    def _get_default_model(self, provider: ProviderType) -> str:
        """Get default model for provider"""
        provider_models = self.llm_service.get_provider_models(provider)
        if not provider_models:
            raise ValueError(f"No models available for provider {provider.value}")

        # Return the first model as default
        return provider_models[0]

    async def _parse_with_llm(
        self,
        timeline_text: str,
        provider: ProviderType,
        model: str,
        api_key: str,
        flexible: bool,
    ) -> List[ParsedEvent]:
        """Parse timeline using LLM provider"""
        # This would integrate with the existing LLM providers
        # For now, return a placeholder implementation
        from ...providers.factory import LLMFactory

        llm_provider = LLMFactory.create_provider(
            provider_name=provider.value, api_key=api_key, model_name=model
        )

        if not llm_provider:
            raise ValueError(f"Failed to create provider: {provider.value}")

        await llm_provider.initialize()
        events = await llm_provider.parse_timeline(timeline_text)

        return events

    def _parse_datetime(
        self, date_str: str, time_str: Optional[str] = None
    ) -> datetime:
        """Parse date and time strings into datetime"""
        # Implementation for parsing date/time strings
        # This is a simplified version
        try:
            if time_str:
                datetime_str = f"{date_str} {time_str}"
                return datetime.fromisoformat(datetime_str)
            else:
                return datetime.fromisoformat(f"{date_str} 00:00:00")
        except ValueError:
            # Fallback parsing logic
            return datetime.now()

    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        import uuid

        return str(uuid.uuid4())
