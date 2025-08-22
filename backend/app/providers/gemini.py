"""
Google Gemini LLM provider implementation.
"""

import json
import asyncio
import logging
from typing import List

from app.providers.base import LLMProvider
from app.domains.calendar.models import ParsedEvent

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Google Gemini AI provider"""

    def __init__(self, api_key: str = None, model_name: str = "gemini-2.0-flash-exp"):
        super().__init__(api_key, model_name)
        self.model = None

    async def initialize(self) -> bool:
        """Initialize Gemini client"""
        try:
            import google.generativeai as genai
            from google.generativeai.types import HarmCategory, HarmBlockThreshold

            if not self.api_key:
                logger.error("Gemini API key not provided")
                return False

            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                },
            )
            logger.info(f"Gemini provider initialized with model: {self.model_name}")
            return True

        except ImportError:
            logger.error("google-generativeai package not installed")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            return False

    def is_available(self) -> bool:
        """Check if Gemini is properly configured"""
        return self.api_key is not None and self.model is not None

    async def parse_timeline(self, timeline_text: str) -> List[ParsedEvent]:
        """Parse timeline using Gemini"""
        if not self.is_available():
            logger.error("Gemini provider not properly initialized")
            return []

        try:
            logger.info(
                f"Parsing timeline with Gemini ({self.model_name}): {timeline_text[:100]}..."
            )

            # Create prompt
            prompt = self._create_parsing_prompt(timeline_text)
            logger.debug(f"Generated prompt: {prompt[:200]}...")

            # Generate response
            logger.info("Calling Gemini API...")
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            logger.info("Gemini API call completed")

            # Parse response
            response_text = response.text.strip()
            logger.info(f"Gemini response: {response_text}")

            # Extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start != -1 and json_end != -1:
                json_text = response_text[json_start:json_end]
                logger.debug(f"Extracted JSON: {json_text}")
                events_data = json.loads(json_text)
            else:
                logger.warning(
                    "No JSON found in response, trying to parse entire response"
                )
                events_data = json.loads(response_text)

            # Convert to ParsedEvent objects
            parsed_events = []
            events_list = events_data.get("events", [])
            logger.info(f"Found {len(events_list)} events in response")

            for i, event_data in enumerate(events_list):
                logger.debug(f"Processing event {i + 1}: {event_data}")
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
                logger.info(
                    f"Parsed event: {parsed_event.title} ({parsed_event.start_date} to {parsed_event.end_date}) - Attendees: {parsed_event.attendees}"
                )

            logger.info(f"Gemini parsed {len(parsed_events)} events successfully")
            return parsed_events

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            logger.error(f"Response was: {response_text}")
            return []
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return []
