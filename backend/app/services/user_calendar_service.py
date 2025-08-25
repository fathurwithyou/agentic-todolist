"""
User-specific Google Calendar service.
Uses the user's stored OAuth tokens to access their Google Calendar.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..domains.auth.models import User
from ..services.google_oauth_service import google_oauth_service
from ..infrastructure.auth_repository import FileAuthRepository

logger = logging.getLogger(__name__)


class UserCalendarService:
    """
    Service for accessing a specific user's Google Calendar.
    """

    def __init__(self, user: User, auth_repository: FileAuthRepository):
        self.user = user
        self.auth_repository = auth_repository
        self.service = None

    def _refresh_token_if_needed(self) -> bool:
        """
        Refresh the user's access token if it's expired.

        Returns:
            True if token is valid/refreshed, False if failed
        """
        if not self.user.google_calendar_token_expiry:
            return False

        # Check if token is expired or will expire soon
        if google_oauth_service.is_token_expired(
            self.user.google_calendar_token_expiry
        ):
            if not self.user.google_calendar_refresh_token:
                logger.error(f"No refresh token available for user {self.user.user_id}")
                return False

            # Refresh the token
            logger.info(f"Refreshing expired token for user {self.user.user_id}")
            token_data = google_oauth_service.refresh_access_token(
                self.user.google_calendar_refresh_token
            )

            if not token_data:
                logger.error(f"Failed to refresh token for user {self.user.user_id}")
                return False

            # Update user with new tokens
            self.user.google_calendar_token = token_data["access_token"]
            if "refresh_token" in token_data:
                self.user.google_calendar_refresh_token = token_data["refresh_token"]

            expires_in = token_data.get("expires_in", 3600)
            self.user.google_calendar_token_expiry = datetime.now() + timedelta(
                seconds=expires_in
            )

            # Save updated user
            self.auth_repository.save_user(self.user)

        return True

    def _get_calendar_service(self):
        """
        Get authenticated Google Calendar service.

        Returns:
            Google Calendar service or None if authentication failed
        """
        if self.service:
            return self.service

        if not self.user.google_calendar_token:
            logger.error(f"No Google Calendar token for user {self.user.user_id}")
            return None

        # Refresh token if needed
        if not self._refresh_token_if_needed():
            return None

        try:
            # Create credentials object
            credentials = google_oauth_service.create_calendar_credentials(
                self.user.google_calendar_token,
                self.user.google_calendar_refresh_token,
                self.user.google_calendar_token_expiry,
            )

            # Build the service
            self.service = build("calendar", "v3", credentials=credentials)
            return self.service

        except Exception as e:
            logger.error(
                f"Failed to create calendar service for user {self.user.user_id}: {e}"
            )
            return None

    def list_calendars(self) -> List[Dict[str, Any]]:
        """
        List the user's Google Calendars.

        Returns:
            List of calendar information
        """
        service = self._get_calendar_service()
        if not service:
            logger.warning(
                f"No calendar service available for user {self.user.user_id}"
            )
            return []

        try:
            calendars_result = service.calendarList().list().execute()
            calendars = calendars_result.get("items", [])

            logger.info(
                f"Found {len(calendars)} calendars for user {self.user.user_id}"
            )

            calendar_list = []
            for cal in calendars:
                calendar_info = {
                    "id": cal["id"],
                    "summary": cal.get("summary", ""),
                    "description": cal.get("description", ""),
                    "primary": cal.get("primary", False),
                    "access_role": cal.get("accessRole", ""),
                    "color_id": cal.get("colorId", ""),
                }
                calendar_list.append(calendar_info)

                # Log each calendar details
                logger.info(
                    f"Calendar: {calendar_info['summary']} (ID: {calendar_info['id']}, "
                    f"Primary: {calendar_info['primary']}, Access: {calendar_info['access_role']})"
                )

            logger.info(
                f"Complete calendar list for user {self.user.user_id}: {calendar_list}"
            )
            return calendar_list

        except HttpError as e:
            logger.error(f"Error listing calendars for user {self.user.user_id}: {e}")
            return []

    def list_writable_calendars(self) -> List[Dict[str, Any]]:
        """
        List only the user's writable Google Calendars (for event creation).

        Returns:
            List of writable calendar information
        """
        all_calendars = self.list_calendars()
        writable_calendars = [
            cal for cal in all_calendars if cal["access_role"] in ["owner", "writer"]
        ]

        logger.info(
            f"Found {len(writable_calendars)} writable calendars for user {self.user.user_id}"
        )
        for cal in writable_calendars:
            logger.info(
                f"Writable calendar: {cal['summary']} (ID: {cal['id']}, Access: {cal['access_role']})"
            )

        return writable_calendars

    def list_events(
        self,
        calendar_id: str = "primary",
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List events from the user's Google Calendar.

        Args:
            calendar_id: Calendar ID to list events from
            time_min: Minimum time to filter events
            time_max: Maximum time to filter events
            max_results: Maximum number of events to return

        Returns:
            List of calendar events
        """
        service = self._get_calendar_service()
        if not service:
            return []

        try:
            # Set default time range if not provided
            if not time_min:
                time_min = datetime.now()
            if not time_max:
                time_max = datetime.now() + timedelta(days=30)

            events_result = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=time_min.isoformat() + "Z",
                    timeMax=time_max.isoformat() + "Z",
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = events_result.get("items", [])

            return [
                {
                    "id": event["id"],
                    "summary": event.get("summary", ""),
                    "description": event.get("description", ""),
                    "start": event.get("start", {}),
                    "end": event.get("end", {}),
                    "location": event.get("location", ""),
                    "attendees": event.get("attendees", []),
                    "html_link": event.get("htmlLink", ""),
                    "created": event.get("created", ""),
                    "updated": event.get("updated", ""),
                    "status": event.get("status", ""),
                }
                for event in events
            ]

        except HttpError as e:
            logger.error(f"Error listing events for user {self.user.user_id}: {e}")
            return []

    def create_event(
        self,
        title: str,
        description: str = "",
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        location: Optional[str] = None,
        calendar_id: str = "primary",
    ) -> Optional[Dict[str, Any]]:
        """
        Create an event in the user's Google Calendar.

        Args:
            title: Event title
            description: Event description
            start_datetime: Event start datetime (for timed events)
            end_datetime: Event end datetime (for timed events)
            start_date: Event start date (for all-day events)
            end_date: Event end date (for all-day events)
            attendees: List of attendee email addresses
            location: Event location
            calendar_id: Calendar ID to create event in

        Returns:
            Created event information or None if failed
        """
        service = self._get_calendar_service()
        if not service:
            return None

        try:
            # Prepare event data
            event_data = {
                "summary": title,
                "description": description,
            }
            
            # Debug: Log the description being sent
            logger.info(f"Creating event with description: {repr(description)}")
            logger.info(f"Description length: {len(description)} characters")

            # Set start and end times
            if start_datetime and end_datetime:
                # Timed event
                event_data["start"] = {
                    "dateTime": start_datetime.isoformat(),
                    "timeZone": "Asia/Jakarta",  # Indonesian timezone (WIIB = UTC+7)
                }
                event_data["end"] = {
                    "dateTime": end_datetime.isoformat(),
                    "timeZone": "Asia/Jakarta",  # Indonesian timezone (WIIB = UTC+7)
                }
            elif start_date:
                # All-day event
                event_data["start"] = {"date": start_date}
                if end_date:
                    event_data["end"] = {"date": end_date}
                else:
                    # Default to same day
                    event_data["end"] = {"date": start_date}
            else:
                raise ValueError("Either datetime or date must be provided")

            # Add optional fields
            if location:
                event_data["location"] = location

            if attendees:
                event_data["attendees"] = [{"email": email} for email in attendees]

            # Create the event
            created_event = (
                service.events()
                .insert(
                    calendarId=calendar_id,
                    body=event_data,
                    sendUpdates="all" if attendees else "none",
                )
                .execute()
            )

            logger.info(
                f"Created event {created_event['id']} for user {self.user.user_id}"
            )
            
            # Debug: Log what Google returned
            logger.info(f"Google Calendar returned description: {repr(created_event.get('description', ''))}")

            return {
                "id": created_event["id"],
                "summary": created_event.get("summary", ""),
                "description": created_event.get("description", ""),
                "start": created_event.get("start", {}),
                "end": created_event.get("end", {}),
                "location": created_event.get("location", ""),
                "attendees": created_event.get("attendees", []),
                "html_link": created_event.get("htmlLink", ""),
                "status": created_event.get("status", ""),
            }

        except HttpError as e:
            logger.error(f"Error creating event for user {self.user.user_id}: {e}")
            return None

    def update_event(
        self,
        event_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        location: Optional[str] = None,
        calendar_id: str = "primary",
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing event in the user's Google Calendar.

        Args:
            event_id: ID of the event to update
            title: New event title
            description: New event description
            start_datetime: New event start datetime (for timed events)
            end_datetime: New event end datetime (for timed events)
            start_date: New event start date (for all-day events)
            end_date: New event end date (for all-day events)
            attendees: New list of attendee email addresses
            location: New event location
            calendar_id: Calendar ID containing the event

        Returns:
            Updated event information or None if failed
        """
        service = self._get_calendar_service()
        if not service:
            return None

        try:
            # Get the existing event
            event = (
                service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            )

            # Update fields if provided
            if title is not None:
                event["summary"] = title
            if description is not None:
                event["description"] = description
            if location is not None:
                event["location"] = location

            # Update time fields if provided
            if start_datetime and end_datetime:
                event["start"] = {
                    "dateTime": start_datetime.isoformat(),
                    "timeZone": "UTC",
                }
                event["end"] = {
                    "dateTime": end_datetime.isoformat(),
                    "timeZone": "UTC",
                }
            elif start_date:
                event["start"] = {"date": start_date}
                if end_date:
                    event["end"] = {"date": end_date}

            if attendees is not None:
                event["attendees"] = [{"email": email} for email in attendees]

            # Update the event
            updated_event = (
                service.events()
                .update(
                    calendarId=calendar_id,
                    eventId=event_id,
                    body=event,
                    sendUpdates="all" if attendees else "none",
                )
                .execute()
            )

            logger.info(f"Updated event {event_id} for user {self.user.user_id}")

            return {
                "id": updated_event["id"],
                "summary": updated_event.get("summary", ""),
                "description": updated_event.get("description", ""),
                "start": updated_event.get("start", {}),
                "end": updated_event.get("end", {}),
                "location": updated_event.get("location", ""),
                "attendees": updated_event.get("attendees", []),
                "html_link": updated_event.get("htmlLink", ""),
                "status": updated_event.get("status", ""),
            }

        except HttpError as e:
            logger.error(
                f"Error updating event {event_id} for user {self.user.user_id}: {e}"
            )
            return None

    def delete_event(self, event_id: str, calendar_id: str = "primary") -> bool:
        """
        Delete an event from the user's Google Calendar.

        Args:
            event_id: ID of the event to delete
            calendar_id: Calendar ID containing the event

        Returns:
            True if event was deleted, False if failed
        """
        service = self._get_calendar_service()
        if not service:
            return False

        try:
            service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            logger.info(f"Deleted event {event_id} for user {self.user.user_id}")
            return True

        except HttpError as e:
            logger.error(
                f"Error deleting event {event_id} for user {self.user.user_id}: {e}"
            )
            return False


def create_user_calendar_service(user: User) -> UserCalendarService:
    """
    Factory function to create a UserCalendarService.

    Args:
        user: User object with calendar tokens

    Returns:
        UserCalendarService instance
    """
    auth_repository = FileAuthRepository()
    return UserCalendarService(user, auth_repository)
