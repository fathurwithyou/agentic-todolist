"""
Abstract base classes for LLM providers.
Defines the contract that all LLM providers must implement.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from app.schemas.events import ParsedEvent

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key
        self.model_name = model_name
        self.client = None

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the LLM client. Returns True if successful."""
        pass

    @abstractmethod
    async def parse_timeline(self, timeline_text: str, system_prompt: Optional[str] = None) -> List[ParsedEvent]:
        """Parse timeline text into structured events."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is properly configured."""
        pass

    def _create_parsing_prompt(self, timeline_text: str, system_prompt: Optional[str] = None) -> str:
        """Create a structured prompt for timeline parsing."""
        context_section = ""
        if system_prompt:
            context_section = f"""
CONTEXT & KNOWLEDGE:
{system_prompt}

"""
        
        return f"""
You are an expert timeline parser. Parse the following timeline text and extract structured event information.

{context_section}TIMELINE TEXT:
{timeline_text}

INSTRUCTIONS:
1. Extract all events with dates, times, and titles
2. Handle both single dates (e.g., "8 September") and date ranges (e.g., "1 Juli–10 Agustus")
3. Extract any time information (e.g., "09:00", "13:30-15:00", "pukul 14:00")
4. Extract any invited participants mentioned (look for "Invite:", "Participants:", etc.)
5. Extract location information (look for "Location:", "Venue:", "Address:", "At:", "di", "tempat", etc.)
6. Extract conference/meeting links (Zoom, Meet, Teams, etc.)
7. Identify event status indicators (confirmed, tentative, cancelled)
8. Look for recurring patterns (daily, weekly, monthly, etc.)
9. Extract reminder/notification preferences
10. Identify event visibility (public, private)
11. Convert all dates to ISO format (YYYY-MM-DD)
12. Convert times to 24-hour format (HH:MM)
13. If no year is mentioned, assume current year ({datetime.now().year})
14. Handle multiple languages (Indonesian, English, etc.)
15. For date ranges, use start date and end date
16. For single dates, use the same date for both start and end
17. If times are provided, extract start_time and end_time; if only one time, use as start_time
18. Accept various time formats: "09:00", "9 AM", "pukul 14:00", "jam 15:30"

REQUIRED OUTPUT FORMAT (JSON only, no other text):
{{
  "events": [
    {{
      "title": "Event Title",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD",
      "start_time": "HH:MM",
      "end_time": "HH:MM",
      "description": "Formatted description, get all information you can",
      "attendees": ["Name1", "Name2"],
      "location": "Event location or venue",
      "all_day": false,
      "status": "confirmed",
      "visibility": "default",
      "transparency": "opaque",
      "colorId": null,
      "recurrence": [],
      "conferenceData": {{
        "conferenceId": "meeting-id",
        "entryPoints": [{{
          "entryPointType": "video",
          "uri": "https://meet.google.com/abc-def-ghi"
        }}]
      }},
      "reminders": {{
        "useDefault": true,
        "overrides": []
      }}
    }}
  ]
}}

IMPORTANT NOTES:
- If no times are specified, set "all_day": true and omit start_time/end_time
- If only one time is given, use it for start_time and estimate end_time (add 1 hour)
- For time ranges like "13:30-15:00", extract both start_time and end_time
- status can be: "confirmed", "tentative", or "cancelled" (default: "confirmed")
- visibility can be: "default", "public", or "private" (default: "default") 
- transparency can be: "opaque" or "transparent" (default: "opaque")
- For conference links, extract the URL and determine type (video, phone, etc.)
- If no conference data, set conferenceData to null
- If no specific reminders mentioned, use default reminders (useDefault: true)

Parse the timeline and return only the JSON response:
"""
