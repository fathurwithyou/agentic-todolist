"""
OpenAI GPT provider implementation.
"""

import json
import logging
from typing import List

from app.providers.base import LLMProvider
from app.domains.calendar.models import ParsedEvent

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""

    def __init__(self, api_key: str = None, model_name: str = "gpt-4o-mini"):
        super().__init__(api_key, model_name)
        self.client = None

    async def initialize(self) -> bool:
        """Initialize OpenAI client"""
        try:
            from openai import AsyncOpenAI

            if not self.api_key:
                logger.error("OpenAI API key not provided")
                return False

            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info(f"OpenAI provider initialized with model: {self.model_name}")
            return True

        except ImportError:
            logger.error("openai package not installed")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
            return False

    def is_available(self) -> bool:
        """Check if OpenAI is properly configured"""
        return self.api_key is not None and self.client is not None

    async def parse_timeline(self, timeline_text: str) -> List[ParsedEvent]:
        """Parse timeline using OpenAI GPT"""
        if not self.is_available():
            logger.error("OpenAI provider not properly initialized")
            return []

        try:
            logger.info(
                f"Parsing timeline with OpenAI ({self.model_name}): {timeline_text[:100]}..."
            )

            # Create prompt
            prompt = self._create_parsing_prompt(timeline_text)

            # Generate response
            logger.info("Calling OpenAI API...")
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            logger.info("OpenAI API call completed")

            # Parse response
            response_text = response.choices[0].message.content.strip()
            logger.info(f"OpenAI response: {response_text}")

            # Extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start != -1 and json_end != -1:
                json_text = response_text[json_start:json_end]
                events_data = json.loads(json_text)
            else:
                events_data = json.loads(response_text)

            # Convert to ParsedEvent objects
            parsed_events = []
            events_list = events_data.get("events", [])
            logger.info(f"Found {len(events_list)} events in response")

            for event_data in events_list:
                parsed_event = ParsedEvent(
                    title=event_data["title"],
                    start_date=event_data["start_date"],
                    end_date=event_data["end_date"],
                    description=event_data.get("description", event_data["title"]),
                    attendees=event_data.get("attendees", []),
                    start_time=event_data.get("start_time"),
                    end_time=event_data.get("end_time"),
                    location=event_data.get("location"),
                    all_day=event_data.get("all_day", True),
                )
                parsed_events.append(parsed_event)

            logger.info(f"OpenAI parsed {len(parsed_events)} events successfully")
            return parsed_events

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI JSON response: {e}")
            return []
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return []
