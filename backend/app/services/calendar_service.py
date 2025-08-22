"""
Google Calendar service implementation.
Handles all Google Calendar API operations with proper error handling and email validation.
"""

import os
import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.schemas.events import ParsedEvent, CreatedEvent
from app.config.settings import get_config

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """
    Service wrapper for Google Calendar API operations.
    Handles authentication and calendar event creation.
    """

    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        service_account_path: Optional[str] = None,
        calendar_id: str = "primary",
    ):
        """
        Initialize Google Calendar service.

        Args:
            credentials_path: Path to OAuth2 credentials file
            service_account_path: Path to service account credentials file
            calendar_id: Calendar ID to create events in (default: primary)
        """
        config = get_config()
        self.credentials_path = credentials_path or config.google.credentials_path
        print(f"Using credentials path: {self.credentials_path}")
        self.service_account_path = (
            service_account_path or config.google.service_account_path
        )
        self.calendar_id = calendar_id or config.google.calendar_id
        self.service = None
        self.creds = None

    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API.

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Try service account authentication first
            if self.service_account_path and os.path.exists(self.service_account_path):
                self.creds = ServiceAccountCredentials.from_service_account_file(
                    self.service_account_path, scopes=self.SCOPES
                )

            # Fall back to OAuth2 user authentication
            elif self.credentials_path and os.path.exists(self.credentials_path):
                creds = None
                token_path = "token.json"

                # Load existing token
                if os.path.exists(token_path):
                    creds = Credentials.from_authorized_user_file(
                        token_path, self.SCOPES
                    )

                # If no valid credentials, get new ones
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_path, self.SCOPES
                        )
                        creds = flow.run_local_server(port=8001)

                    # Save credentials for next run
                    with open(token_path, "w") as token:
                        token.write(creds.to_json())

                self.creds = creds

            else:
                raise ValueError("No valid credentials path provided")

            # Build the service
            self.service = build("calendar", "v3", credentials=self.creds)
            return True

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False

    def _convert_date_to_datetime(
        self, date_str: str, is_end_date: bool = False
    ) -> Dict[str, str]:
        """
        Convert date string to Google Calendar datetime format.

        Args:
            date_str: Date in YYYY-MM-DD format or YYYY-MM-DDTHH:MM:SS format
            is_end_date: If True, set time to end of day for all-day events

        Returns:
            Dictionary with date/dateTime for Google Calendar API
        """
        try:
            # Check if it's a datetime string with time component
            if "T" in date_str:
                # It's a datetime string, use dateTime format
                parsed_datetime = datetime.fromisoformat(date_str)
                return {
                    "dateTime": parsed_datetime.isoformat(),
                    "timeZone": "UTC",  # You may want to make this configurable
                }
            else:
                # It's just a date string, use date format for all-day events
                parsed_date = datetime.fromisoformat(date_str)

                if is_end_date:
                    # For end dates, add one day for all-day events
                    from datetime import timedelta

                    next_day = parsed_date + timedelta(days=1)
                    return {"date": next_day.strftime("%Y-%m-%d")}
                else:
                    return {"date": parsed_date.strftime("%Y-%m-%d")}

        except ValueError:
            # Fallback to current date
            today = datetime.now().strftime("%Y-%m-%d")
            return {"date": today}

    def _is_valid_email(self, email: str) -> bool:
        """
        Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            True if email is valid format, False otherwise
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def _map_attendees_to_emails(self, attendees: List[str]) -> List[Dict[str, str]]:
        """
        Map attendee names to email addresses with validation.

        Args:
            attendees: List of attendee names or emails

        Returns:
            List of valid attendee dictionaries for Google Calendar API
        """
        config = get_config()

        attendee_list = []
        for name_or_email in attendees:
            name_or_email = name_or_email.strip()

            # Check if it's already an email
            if self._is_valid_email(name_or_email):
                email = name_or_email
                display_name = name_or_email.split("@")[
                    0
                ]  # Use part before @ as display name
            else:
                # Map name to email using config
                email = config.get_email_for_attendee(name_or_email)
                display_name = name_or_email

            # Validate email before adding
            if self._is_valid_email(email):
                attendee_list.append({"email": email, "displayName": display_name})
                logger.info(f"Added valid attendee: {display_name} <{email}>")
            else:
                logger.warning(
                    f"Skipping invalid email: {email} for attendee: {name_or_email}"
                )

        return attendee_list

    async def create_event(self, event: ParsedEvent) -> Optional[CreatedEvent]:
        """
        Create a single Google Calendar event.

        Args:
            event: Parsed event data

        Returns:
            Created event info or None if failed
        """
        if not self.service:
            if not self.authenticate():
                return None

        try:
            # Prepare event data
            start_datetime = self._convert_date_to_datetime(event.start_date)
            end_datetime = self._convert_date_to_datetime(
                event.end_date, is_end_date=True
            )
            attendees = self._map_attendees_to_emails(event.attendees)

            calendar_event = {
                "summary": event.title,
                "description": event.description,
                "start": start_datetime,
                "end": end_datetime,
            }

            # Add attendees if any
            if attendees:
                calendar_event["attendees"] = attendees

            # Create the event with sendUpdates to send invitations
            logger.info(f"Creating calendar event: {event.title}")
            logger.debug(f"Event data: {calendar_event}")

            created_event = (
                self.service.events()
                .insert(
                    calendarId=self.calendar_id,
                    body=calendar_event,
                    sendUpdates="all",  # Send email invitations to all attendees
                )
                .execute()
            )

            logger.info(f"Event created successfully: {created_event['id']}")

            return CreatedEvent(
                id=created_event["id"],
                summary=created_event["summary"],
                start_date=event.start_date,
                end_date=event.end_date,
                html_link=created_event.get("htmlLink", ""),
            )

        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            logger.error(f"Failed to create event: {event.title}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating event: {e}")
            logger.error(f"Failed to create event: {event.title}")
            return None

    async def create_events(self, events: List[ParsedEvent]) -> List[CreatedEvent]:
        """
        Create multiple Google Calendar events.

        Args:
            events: List of parsed events

        Returns:
            List of successfully created events
        """
        created_events = []

        for event in events:
            created_event = await self.create_event(event)
            if created_event:
                created_events.append(created_event)

        return created_events

    def list_calendars(self) -> List[Dict[str, Any]]:
        """
        List available calendars for the authenticated user.

        Returns:
            List of calendar information
        """
        if not self.service:
            if not self.authenticate():
                return []

        try:
            calendars_result = self.service.calendarList().list().execute()
            calendars = calendars_result.get("items", [])

            return [
                {
                    "id": cal["id"],
                    "summary": cal["summary"],
                    "primary": cal.get("primary", False),
                }
                for cal in calendars
            ]

        except HttpError as e:
            logger.error(f"Error listing calendars: {e}")
            return []


# Global calendar service instance
calendar_service = GoogleCalendarService()


async def create_calendar_events(events: List[ParsedEvent]) -> List[CreatedEvent]:
    """
    Convenience function to create calendar events.

    Args:
        events: List of parsed events

    Returns:
        List of created events
    """
    return await calendar_service.create_events(events)
