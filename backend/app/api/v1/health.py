"""
Health check API endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException, status

from app.schemas.health import HealthResponse
from app.domains.llm.service import LLMService
from app.domains.llm.encryption import APIKeyEncryption
from app.infrastructure.llm_repository import FileLLMRepository

logger = logging.getLogger(__name__)

# Initialize LLM service
llm_repository = FileLLMRepository()
encryption = APIKeyEncryption()
llm_service = LLMService(llm_repository, encryption)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check LLM configuration
        llm_providers = llm_service.get_available_providers()
        llm_configured = len(llm_providers) > 0

        # Calendar authentication is checked per user
        calendar_authenticated = True  # Always available for authenticated users

        return HealthResponse(
            status="healthy"
            if llm_configured and calendar_authenticated
            else "degraded",
            llm_configured=llm_configured,
            calendar_authenticated=calendar_authenticated,
            llm_providers={"providers": llm_providers},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}",
        )
