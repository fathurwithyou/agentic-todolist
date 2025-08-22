"""
LLM repository interface.
Defines data access patterns for LLM domain.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from .models import APIKey, ProviderType


class LLMRepository(ABC):
    """
    LLM repository interface.
    Defines how LLM-related data is stored and retrieved.
    """

    @abstractmethod
    def save_api_key(self, api_key: APIKey) -> APIKey:
        """Save or update an API key"""
        pass

    @abstractmethod
    def get_api_key(self, user_id: str, provider: ProviderType) -> Optional[APIKey]:
        """Get API key for user and provider"""
        pass

    @abstractmethod
    def has_api_key(self, user_id: str, provider: ProviderType) -> bool:
        """Check if user has API key for provider"""
        pass

    @abstractmethod
    def remove_api_key(self, user_id: str, provider: ProviderType) -> bool:
        """Remove API key for user and provider"""
        pass

    @abstractmethod
    def list_user_api_keys(self, user_id: str) -> List[APIKey]:
        """List all API keys for a user"""
        pass
