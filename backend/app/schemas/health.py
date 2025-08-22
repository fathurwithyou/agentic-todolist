"""
Health check related schemas.
"""

from pydantic import BaseModel
from typing import Dict, Any


class HealthResponse(BaseModel):
    """Health check response schema"""

    status: str
    llm_configured: bool
    calendar_authenticated: bool
    llm_providers: Dict[str, Any]
