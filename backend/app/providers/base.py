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
1. Extract all events with dates and titles
2. Handle both single dates (e.g., "8 September") and date ranges (e.g., "1 Juli–10 Agustus")
3. Extract any invited participants mentioned (look for "Invite:", "Participants:", etc.)
4. Convert all dates to ISO format (YYYY-MM-DD)
5. If no year is mentioned, assume current year ({datetime.now().year})
6. Handle multiple languages (Indonesian, English, etc.)
7. For date ranges, use start date and end date
8. For single dates, use the same date for both start and end

REQUIRED OUTPUT FORMAT (JSON only, no other text):
{{
  "events": [
    {{
      "title": "Event Title",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD", 
      "description": "Original event line from timeline",
      "attendees": ["Name1", "Name2"]
    }}
  ]
}}

MONTH MAPPINGS:
- januari/jan = January
- februari/feb = February  
- maret/mar = March
- april/apr = April
- mei = May
- juni/jun = June
- juli/jul = July
- agustus/agu = August
- september/sep = September
- oktober/okt = October
- november/nov = November
- desember/des = December

Parse the timeline and return only the JSON response:
"""
