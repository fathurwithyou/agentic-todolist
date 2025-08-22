"""
Clean LLM API endpoints.
Uses domain services for API key management.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict

from ..domains.llm.service import LLMService
from ..domains.llm.models import ProviderType
from ..domains.llm.encryption import APIKeyEncryption
from ..infrastructure.llm_repository import FileLLMRepository
from .auth import get_current_user

logger = logging.getLogger(__name__)

# Initialize dependencies
llm_repository = FileLLMRepository()
encryption = APIKeyEncryption()
llm_service = LLMService(llm_repository, encryption)

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


class SaveAPIKeyRequest(BaseModel):
    """Request to save an API key"""

    provider: str
    api_key: str


class APIKeyResponse(BaseModel):
    """Response for API key operations"""

    success: bool
    message: str
    provider: str


class APIKeysListResponse(BaseModel):
    """Response listing saved API keys"""

    api_keys: Dict[str, bool]  # provider -> has_key


@router.post("/save", response_model=APIKeyResponse)
async def save_api_key(
    request: SaveAPIKeyRequest, current_user=Depends(get_current_user)
):
    """Save an API key for the authenticated user"""
    try:
        # Convert string to enum
        try:
            provider = ProviderType(request.provider.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported provider: {request.provider}. Supported: gemini, openai",
            )

        # Save API key using domain service
        llm_service.save_api_key(
            user_id=current_user.user.user_id,
            provider=provider,
            api_key=request.api_key,
        )

        return APIKeyResponse(
            success=True,
            message=f"API key saved securely for {request.provider}",
            provider=request.provider,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to save API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to save API key")


@router.get("/list", response_model=APIKeysListResponse)
async def list_api_keys(current_user=Depends(get_current_user)):
    """List which providers have API keys saved"""
    try:
        has_keys = llm_service.list_user_providers(current_user.user.user_id)
        return APIKeysListResponse(api_keys=has_keys)

    except Exception as e:
        logger.error(f"Failed to list API keys: {e}")
        raise HTTPException(status_code=500, detail="Failed to list API keys")


@router.get("/test/{provider}")
async def test_api_key(provider: str, current_user=Depends(get_current_user)):
    """Test if an API key is valid"""
    try:
        # Convert string to enum
        try:
            provider_enum = ProviderType(provider.lower())
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Unsupported provider: {provider}"
            )

        result = llm_service.test_api_key(current_user.user.user_id, provider_enum)
        return result

    except Exception as e:
        logger.error(f"API key test failed: {e}")
        raise HTTPException(status_code=500, detail="API key test failed")


@router.delete("/remove/{provider}")
async def remove_api_key(provider: str, current_user=Depends(get_current_user)):
    """Remove an API key"""
    try:
        # Convert string to enum
        try:
            provider_enum = ProviderType(provider.lower())
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Unsupported provider: {provider}"
            )

        success = llm_service.remove_api_key(current_user.user.user_id, provider_enum)

        if success:
            return {
                "success": True,
                "message": f"API key removed for {provider}",
                "provider": provider,
            }
        else:
            raise HTTPException(
                status_code=404, detail=f"No API key found for provider {provider}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove API key")


@router.get("/providers")
async def get_available_providers():
    """Get list of available LLM providers"""
    try:
        providers = llm_service.get_available_providers()
        return {
            "available_providers": [p["name"] for p in providers],
            "provider_models": {p["name"]: p["models"] for p in providers},
        }
    except Exception as e:
        logger.error(f"Failed to get providers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get providers")
