"""
Health check API endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException, status

from app.schemas.health import HealthResponse
from app.services.llm_service import llm_service
from app.services.calendar_service import calendar_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check LLM configuration
        llm_status = llm_service.get_provider_status()
        llm_configured = llm_status["initialized"]

        # Check calendar authentication
        calendar_authenticated = calendar_service.creds is not None

        return HealthResponse(
            status="healthy"
            if llm_configured and calendar_authenticated
            else "degraded",
            llm_configured=llm_configured,
            calendar_authenticated=calendar_authenticated,
            llm_providers=llm_status,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}",
        )
