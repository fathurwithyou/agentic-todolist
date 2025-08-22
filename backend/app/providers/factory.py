"""
Factory for creating LLM provider instances.
"""

import logging
from typing import Optional, List

from app.providers.base import LLMProvider
from app.providers.gemini import GeminiProvider
from app.providers.openai import OpenAIProvider

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory for creating LLM providers"""

    PROVIDERS = {
        "gemini": GeminiProvider,
        "openai": OpenAIProvider,
    }

    @classmethod
    def create_provider(
        cls,
        provider_name: str,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> Optional[LLMProvider]:
        """Create an LLM provider instance"""
        provider_name = provider_name.lower()

        if provider_name not in cls.PROVIDERS:
            logger.error(
                f"Unknown provider: {provider_name}. Available: {list(cls.PROVIDERS.keys())}"
            )
            return None

        provider_class = cls.PROVIDERS[provider_name]

        # Use default model names if not specified
        if model_name is None:
            if provider_name == "gemini":
                model_name = "gemini-2.0-flash-exp"
            elif provider_name == "openai":
                model_name = "gpt-4o-mini"

        return provider_class(api_key=api_key, model_name=model_name)

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available provider names"""
        return list(cls.PROVIDERS.keys())
