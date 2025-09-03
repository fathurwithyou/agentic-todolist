"""
OpenAI GPT provider implementation.
"""

import json
import logging
from typing import List, Optional

from app.providers.base import LLMProvider
from app.domains.calendar.models import (
    ParsedEvent,
    EventStatus,
    EventVisibility,
    EventTransparency,
    ConferenceData,
    ConferenceEntryPoint,
    Reminders,
)
from app.domains.task.models import ParsedTask, TaskPriority

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

    async def parse_timeline(self, timeline_text: str, system_prompt: Optional[str] = None) -> List[ParsedEvent]:
        """Parse timeline using OpenAI GPT"""
        if not self.is_available():
            logger.error("OpenAI provider not properly initialized")
            return []

        try:
            logger.info(
                f"Parsing timeline with OpenAI ({self.model_name}): {timeline_text[:100]}..."
            )

            # Create prompt
            prompt = self._create_parsing_prompt(timeline_text, system_prompt)

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
                # Parse status
                status_str = event_data.get("status", "confirmed")
                status = EventStatus.CONFIRMED
                if status_str == "tentative":
                    status = EventStatus.TENTATIVE
                elif status_str == "cancelled":
                    status = EventStatus.CANCELLED

                # Parse visibility
                visibility_str = event_data.get("visibility", "default")
                visibility = EventVisibility.DEFAULT
                if visibility_str == "public":
                    visibility = EventVisibility.PUBLIC
                elif visibility_str == "private":
                    visibility = EventVisibility.PRIVATE

                # Parse transparency
                transparency_str = event_data.get("transparency", "opaque")
                transparency = EventTransparency.OPAQUE
                if transparency_str == "transparent":
                    transparency = EventTransparency.TRANSPARENT

                # Parse conference data
                conference_data = None
                conference_raw = event_data.get("conferenceData")
                if conference_raw:
                    entry_points = []
                    for ep_data in conference_raw.get("entryPoints", []):
                        entry_point = ConferenceEntryPoint(
                            entryPointType=ep_data.get("entryPointType", "video"),
                            uri=ep_data.get("uri"),
                            label=ep_data.get("label"),
                            pin=ep_data.get("pin"),
                            accessCode=ep_data.get("accessCode"),
                            meetingCode=ep_data.get("meetingCode"),
                            passcode=ep_data.get("passcode"),
                            password=ep_data.get("password"),
                        )
                        entry_points.append(entry_point)

                    conference_data = ConferenceData(
                        conferenceId=conference_raw.get("conferenceId"),
                        entryPoints=entry_points,
                        signature=conference_raw.get("signature"),
                        notes=conference_raw.get("notes"),
                    )

                # Parse reminders
                reminders_data = event_data.get("reminders", {"useDefault": True})
                reminders = Reminders(
                    useDefault=reminders_data.get("useDefault", True),
                    overrides=[],  # Could be extended to parse overrides
                )

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
                    status=status,
                    visibility=visibility,
                    transparency=transparency,
                    colorId=event_data.get("colorId"),
                    recurrence=event_data.get("recurrence", []),
                    reminders=reminders,
                    conferenceData=conference_data,
                    sequence=event_data.get("sequence", 0),
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

    async def parse_timeline_for_tasks(self, timeline_text: str, system_prompt: Optional[str] = None) -> List[ParsedTask]:
        """Parse timeline using OpenAI for tasks"""
        if not self.is_available():
            logger.error("OpenAI provider not properly initialized")
            return []

        try:
            logger.info(f"Parsing timeline for tasks with OpenAI ({self.model_name}): {timeline_text[:100]}...")

            # Create task parsing prompt
            prompt = self._create_task_parsing_prompt(timeline_text, system_prompt)

            # Make API call
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )

            response_text = response.choices[0].message.content.strip()
            logger.info(f"OpenAI task response: {response_text}")

            # Extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start != -1 and json_end != -1:
                json_text = response_text[json_start:json_end]
                tasks_data = json.loads(json_text)
            else:
                logger.warning("No JSON found in response, trying to parse entire response")
                tasks_data = json.loads(response_text)

            # Convert to ParsedTask objects
            parsed_tasks = []
            for task_data in tasks_data.get("tasks", []):
                try:
                    priority = None
                    if task_data.get("priority"):
                        priority = TaskPriority(task_data["priority"])

                    parsed_task = ParsedTask(
                        title=task_data["title"],
                        notes=task_data.get("notes"),
                        priority=priority,
                        due_date=task_data.get("due_date"),
                        due_time=task_data.get("due_time"),
                        completed=task_data.get("completed", False),
                        parent_task=task_data.get("parent_task"),
                    )
                    parsed_tasks.append(parsed_task)
                    logger.info(f"Parsed task: {parsed_task.title} (due: {parsed_task.due_date})")

                except Exception as e:
                    logger.error(f"Failed to parse task data {task_data}: {e}")
                    continue

            logger.info(f"OpenAI parsed {len(parsed_tasks)} tasks successfully")
            return parsed_tasks

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI JSON response: {e}")
            return []
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return []
