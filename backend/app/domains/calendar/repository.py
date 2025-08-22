"""
Calendar repository interface.
Defines data access patterns for calendar domain.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from .models import CalendarEvent


class CalendarRepository(ABC):
    """
    Calendar repository interface.
    Defines how calendar data is stored and retrieved.
    """

    @abstractmethod
    def save_event(self, event: CalendarEvent) -> CalendarEvent:
        """Save or update a calendar event"""
        pass

    @abstractmethod
    def get_event(self, event_id: str) -> Optional[CalendarEvent]:
        """Get event by ID"""
        pass

    @abstractmethod
    def get_user_events(self, user_id: str) -> List[CalendarEvent]:
        """Get all events for a user"""
        pass

    @abstractmethod
    def get_events_by_date_range(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> List[CalendarEvent]:
        """Get events within date range for user"""
        pass

    @abstractmethod
    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        pass

    @abstractmethod
    def update_event(self, event: CalendarEvent) -> CalendarEvent:
        """Update an existing event"""
        pass
