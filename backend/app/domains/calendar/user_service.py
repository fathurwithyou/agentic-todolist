"""
User calendar service for Google Calendar operations.
Moved from app/services to domains for clean architecture.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..auth.models import User
from ...infrastructure.auth_repository import AuthRepository

logger = logging.getLogger(__name__)


class UserCalendarService:
    """Service for user-specific Google Calendar operations"""
    
    def __init__(self, user: User, auth_repository: AuthRepository):
        self.user = user
        self.auth_repository = auth_repository
        self.service = None
        self._initialize_google_service()
    
    def _initialize_google_service(self):
        """Initialize Google Calendar service for the user"""
        try:
            from googleapiclient.discovery import build
            
            # Get user's Google credentials
            creds = self.auth_repository.get_user_credentials(self.user.user_id)
            if creds and creds.valid:
                self.service = build('calendar', 'v3', credentials=creds)
                logger.info(f"Google Calendar service initialized for user {self.user.user_id}")
            else:
                logger.warning(f"No valid credentials for user {self.user.user_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {e}")
    
    def list_calendars(self) -> List[Dict[str, Any]]:
        """List user's Google Calendars"""
        if not self.service:
            return []
        
        try:
            result = self.service.calendarList().list().execute()
            calendars = result.get('items', [])
            
            return [
                {
                    "id": cal["id"],
                    "summary": cal["summary"],
                    "description": cal.get("description", ""),
                    "primary": cal.get("primary", False),
                    "access_role": cal.get("accessRole", ""),
                    "color_id": cal.get("colorId", ""),
                }
                for cal in calendars
            ]
        except Exception as e:
            logger.error(f"Failed to list calendars: {e}")
            return []
    
    def list_writable_calendars(self) -> List[Dict[str, Any]]:
        """List user's writable Google Calendars"""
        calendars = self.list_calendars()
        return [cal for cal in calendars if cal["access_role"] in ["owner", "writer"]]
    
    def create_event_from_parsed(self, parsed_event, calendar_id: str = "primary") -> Optional[Dict[str, Any]]:
        """Create event from ParsedEvent object"""
        if not self.service:
            return None
        
        try:
            # Convert ParsedEvent to Google Calendar event format
            event_body = {
                'summary': parsed_event.title,
                'description': parsed_event.description,
                'location': parsed_event.location,
            }
            
            # Handle date/time
            if parsed_event.all_day:
                event_body['start'] = {'date': parsed_event.start_date}
                event_body['end'] = {'date': parsed_event.end_date}
            else:
                start_dt = f"{parsed_event.start_date}T{parsed_event.start_time or '00:00:00'}"
                end_dt = f"{parsed_event.end_date}T{parsed_event.end_time or '23:59:59'}"
                event_body['start'] = {'dateTime': start_dt}
                event_body['end'] = {'dateTime': end_dt}
            
            # Add attendees
            if parsed_event.attendees:
                event_body['attendees'] = [{'email': email} for email in parsed_event.attendees]
            
            result = self.service.events().insert(calendarId=calendar_id, body=event_body).execute()
            logger.info(f"Created Google Calendar event: {result['id']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create event from parsed data: {e}")
            return None
    
    def list_events(self, calendar_id: str = "primary", time_min=None, time_max=None, max_results: int = 100) -> List[Dict[str, Any]]:
        """List events from Google Calendar"""
        if not self.service:
            return []
        
        try:
            params = {
                'calendarId': calendar_id,
                'maxResults': max_results,
                'singleEvents': True,
                'orderBy': 'startTime'
            }
            
            if time_min:
                params['timeMin'] = time_min.isoformat() + 'Z'
            if time_max:
                params['timeMax'] = time_max.isoformat() + 'Z'
            
            result = self.service.events().list(**params).execute()
            events = result.get('items', [])
            
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
        except Exception as e:
            logger.error(f"Failed to list events: {e}")
            return []
    
    def create_event(self, title: str, description: str = "", start_datetime=None, end_datetime=None, 
                    start_date=None, end_date=None, attendees=None, location=None, 
                    calendar_id: str = "primary") -> Optional[Dict[str, Any]]:
        """Create event in Google Calendar"""
        if not self.service:
            return None
        
        try:
            event_body = {
                'summary': title,
                'description': description,
                'location': location,
            }
            
            # Handle date/time
            if start_date and end_date:
                event_body['start'] = {'date': start_date}
                event_body['end'] = {'date': end_date}
            elif start_datetime and end_datetime:
                event_body['start'] = {'dateTime': start_datetime.isoformat()}
                event_body['end'] = {'dateTime': end_datetime.isoformat()}
            
            # Add attendees
            if attendees:
                event_body['attendees'] = [{'email': email} for email in attendees]
            
            result = self.service.events().insert(calendarId=calendar_id, body=event_body).execute()
            logger.info(f"Created Google Calendar event: {result['id']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            return None
    
    def update_event(self, event_id: str, calendar_id: str = "primary", **kwargs) -> Optional[Dict[str, Any]]:
        """Update event in Google Calendar"""
        if not self.service:
            return None
        
        try:
            # Get existing event
            event = self.service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            
            # Update fields
            if 'title' in kwargs and kwargs['title']:
                event['summary'] = kwargs['title']
            if 'description' in kwargs and kwargs['description']:
                event['description'] = kwargs['description']
            if 'location' in kwargs:
                event['location'] = kwargs['location']
            
            # Handle datetime updates
            if 'start_datetime' in kwargs and kwargs['start_datetime']:
                event['start'] = {'dateTime': kwargs['start_datetime'].isoformat()}
            if 'end_datetime' in kwargs and kwargs['end_datetime']:
                event['end'] = {'dateTime': kwargs['end_datetime'].isoformat()}
            if 'start_date' in kwargs and kwargs['start_date']:
                event['start'] = {'date': kwargs['start_date']}
            if 'end_date' in kwargs and kwargs['end_date']:
                event['end'] = {'date': kwargs['end_date']}
            
            # Update attendees
            if 'attendees' in kwargs and kwargs['attendees']:
                event['attendees'] = [{'email': email} for email in kwargs['attendees']]
            
            result = self.service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
            logger.info(f"Updated Google Calendar event: {event_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update event: {e}")
            return None
    
    def delete_event(self, event_id: str, calendar_id: str = "primary") -> bool:
        """Delete event from Google Calendar"""
        if not self.service:
            return False
        
        try:
            self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            logger.info(f"Deleted Google Calendar event: {event_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete event: {e}")
            return False


def create_user_calendar_service(user: User) -> UserCalendarService:
    """Factory function to create UserCalendarService"""
    from ...infrastructure.auth_repository import FileAuthRepository
    auth_repository = FileAuthRepository()
    return UserCalendarService(user, auth_repository)