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
    async def parse_timeline(self, timeline_text: str) -> List[ParsedEvent]:
        """Parse timeline text into structured events."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is properly configured."""
        pass

    def _create_parsing_prompt(self, timeline_text: str) -> str:
        """Create a structured prompt for timeline parsing."""
        return f"""
You are an expert timeline parser. Parse the following timeline text and extract structured event information.

TIMELINE TEXT:
{timeline_text}

INSTRUCTIONS:
1. Extract all events with dates, times, and titles
2. Handle both single dates (e.g., "8 September") and date ranges (e.g., "1 Juli–10 Agustus")
3. Extract any time information (e.g., "09:00", "13:30-15:00", "pukul 14:00")
4. Extract any invited participants mentioned (look for "Invite:", "Participants:", etc.)
5. Convert all dates to ISO format (YYYY-MM-DD)
6. Convert times to 24-hour format (HH:MM)
7. If no year is mentioned, assume current year ({datetime.now().year})
8. Handle multiple languages (Indonesian, English, etc.)
9. For date ranges, use start date and end date
10. For single dates, use the same date for both start and end
11. If times are provided, extract start_time and end_time; if only one time, use as start_time
12. Accept various time formats: "09:00", "9 AM", "pukul 14:00", "jam 15:30"

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
      "all_day": false
    }}
  ]
}}

IMPORTANT NOTES:
- If no times are specified, set "all_day": true and omit start_time/end_time
- If only one time is given, use it for start_time and estimate end_time (add 1 hour)
- For time ranges like "13:30-15:00", extract both start_time and end_time

Parse the timeline and return only the JSON response:
"""
