"""
LLM domain service.
Handles LLM providers and API key management.
"""

import logging
from typing import Optional, Dict, List
from datetime import datetime

from .models import APIKey, ProviderType, LLMProvider
from .repository import LLMRepository
from .encryption import APIKeyEncryption

logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM domain service.
    Manages API keys and LLM provider interactions.
    """

    # Supported providers configuration
    PROVIDERS = {
        ProviderType.GEMINI: LLMProvider(
            name=ProviderType.GEMINI,
            display_name="Google Gemini",
            models=[
                "gemini-2.0-flash-exp",
                "gemini-2.5-flash",
                "gemini-1.5-pro",
                "gemini-1.5-flash",
            ],
            default_model="gemini-2.0-flash-exp",
        ),
        ProviderType.OPENAI: LLMProvider(
            name=ProviderType.OPENAI,
            display_name="OpenAI",
            models=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
            default_model="gpt-4o-mini",
            api_base_url="https://api.openai.com/v1",
        ),
    }

    def __init__(self, repository: LLMRepository, encryption: APIKeyEncryption):
        self.repository = repository
        self.encryption = encryption

    def save_api_key(
        self, user_id: str, provider: ProviderType, api_key: str
    ) -> APIKey:
        """Save encrypted API key for user"""
        # Validate provider
        if provider not in self.PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider.value}")

        # Validate API key format
        if len(api_key.strip()) < 10:
            raise ValueError("API key appears to be invalid (too short)")

        # Encrypt the API key
        encrypted_key = self.encryption.encrypt(api_key)
        key_hash = APIKey.create_hash(api_key)

        # Create API key entity
        now = datetime.now()
        api_key_entity = APIKey(
            user_id=user_id,
            provider=provider,
            api_key_hash=key_hash,
            encrypted_api_key=encrypted_key,
            created_at=now,
            updated_at=now,
        )

        # Save to repository
        saved_key = self.repository.save_api_key(api_key_entity)
        logger.info(f"API key saved for user {user_id}, provider {provider.value}")

        return saved_key

    def get_api_key(self, user_id: str, provider: ProviderType) -> Optional[str]:
        """Get decrypted API key for user and provider"""
        api_key_entity = self.repository.get_api_key(user_id, provider)

        if not api_key_entity or not api_key_entity.is_active:
            return None

        try:
            return self.encryption.decrypt(api_key_entity.encrypted_api_key)
        except Exception as e:
            logger.error(f"Failed to decrypt API key for user {user_id}: {e}")
            return None

    def has_api_key(self, user_id: str, provider: ProviderType) -> bool:
        """Check if user has API key for provider"""
        return self.repository.has_api_key(user_id, provider)

    def list_user_providers(self, user_id: str) -> Dict[str, bool]:
        """List which providers have API keys for user"""
        result = {}
        for provider in self.PROVIDERS:
            result[provider.value] = self.has_api_key(user_id, provider)
        return result

    def remove_api_key(self, user_id: str, provider: ProviderType) -> bool:
        """Remove API key for user and provider"""
        success = self.repository.remove_api_key(user_id, provider)
        if success:
            logger.info(
                f"API key removed for user {user_id}, provider {provider.value}"
            )
        return success

    def test_api_key(self, user_id: str, provider: ProviderType) -> Dict:
        """Test if API key is valid by making a test request"""
        api_key = self.get_api_key(user_id, provider)
        if not api_key:
            return {
                "success": False,
                "message": f"No API key found for provider {provider.value}",
            }

        try:
            # Import here to avoid circular dependencies
            if provider == ProviderType.GEMINI:
                return self._test_gemini_key(api_key)
            elif provider == ProviderType.OPENAI:
                return self._test_openai_key(api_key)
            else:
                return {
                    "success": False,
                    "message": f"Testing not implemented for {provider.value}",
                }
        except Exception as e:
            logger.error(f"API key test failed for {provider.value}: {e}")
            return {"success": False, "message": f"API key test failed: {str(e)}"}

    def get_available_providers(self) -> List[Dict]:
        """Get list of available providers"""
        return [
            {
                "name": provider.name.value,
                "display_name": provider.display_name,
                "models": provider.models,
                "default_model": provider.default_model,
            }
            for provider in self.PROVIDERS.values()
        ]

    def get_provider_models(self, provider: ProviderType) -> List[str]:
        """Get available models for a provider"""
        if provider in self.PROVIDERS:
            return self.PROVIDERS[provider].models
        return []

    async def get_dynamic_provider_models(self, provider: ProviderType, api_key: str) -> List[str]:
        """Get available models dynamically from provider API"""
        if provider == ProviderType.GEMINI:
            return await self._get_gemini_models(api_key)
        else:
            # Fallback to static list for other providers
            return self.get_provider_models(provider)

    async def _get_gemini_models(self, api_key: str) -> List[str]:
        """Get Gemini models dynamically from API"""
        import asyncio
        import google.generativeai as genai
        
        def _fetch_models():
            genai.configure(api_key=api_key)
            models = genai.list_models()
            return [model.name.replace("models/", "") for model in models if 'generateContent' in model.supported_generation_methods]
        
        try:
            models = await asyncio.to_thread(_fetch_models)
            logger.info(f"Fetched {len(models)} Gemini models dynamically")
            return models
        except Exception as e:
            logger.error(f"Failed to fetch Gemini models dynamically: {e}")
            # Fallback to static list
            return self.PROVIDERS[ProviderType.GEMINI].models

    def _test_gemini_key(self, api_key: str) -> Dict:
        """Test Gemini API key"""
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        models = genai.list_models()
        model_count = len(list(models))

        return {
            "success": True,
            "message": f"Gemini API key is valid. Found {model_count} models.",
        }

    def _test_openai_key(self, api_key: str) -> Dict:
        """Test OpenAI API key"""
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        models = client.models.list()
        model_count = len(models.data)

        return {
            "success": True,
            "message": f"OpenAI API key is valid. Found {model_count} models.",
        }
