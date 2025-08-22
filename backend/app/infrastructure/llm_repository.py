"""
LLM repository implementation.
File-based storage for API keys and LLM data.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional

from ..domains.llm.repository import LLMRepository
from ..domains.llm.models import APIKey, ProviderType

logger = logging.getLogger(__name__)


class FileLLMRepository(LLMRepository):
    """
    File-based LLM repository.
    Stores API keys in JSON file.
    """

    def __init__(self, data_dir: str = "data/llm"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.api_keys_file = self.data_dir / "api_keys.json"

    def save_api_key(self, api_key: APIKey) -> APIKey:
        """Save or update an API key"""
        api_keys = self._load_api_keys()

        # Remove existing key for same user/provider
        api_keys = [
            key
            for key in api_keys
            if not (
                key["user_id"] == api_key.user_id
                and key["provider"] == api_key.provider.value
            )
        ]

        # Add new key
        api_keys.append(api_key.to_dict())

        self._save_api_keys(api_keys)
        logger.info(
            f"Saved API key for user {api_key.user_id}, provider {api_key.provider.value}"
        )
        return api_key

    def get_api_key(self, user_id: str, provider: ProviderType) -> Optional[APIKey]:
        """Get API key for user and provider"""
        api_keys = self._load_api_keys()

        for key_data in api_keys:
            if (
                key_data["user_id"] == user_id
                and key_data["provider"] == provider.value
                and key_data["is_active"]
            ):
                return APIKey.from_dict(key_data)

        return None

    def has_api_key(self, user_id: str, provider: ProviderType) -> bool:
        """Check if user has API key for provider"""
        return self.get_api_key(user_id, provider) is not None

    def remove_api_key(self, user_id: str, provider: ProviderType) -> bool:
        """Remove API key for user and provider"""
        api_keys = self._load_api_keys()
        found = False

        for key_data in api_keys:
            if (
                key_data["user_id"] == user_id
                and key_data["provider"] == provider.value
                and key_data["is_active"]
            ):
                key_data["is_active"] = False
                found = True
                break

        if found:
            self._save_api_keys(api_keys)
            logger.info(
                f"Removed API key for user {user_id}, provider {provider.value}"
            )

        return found

    def list_user_api_keys(self, user_id: str) -> List[APIKey]:
        """List all API keys for a user"""
        api_keys = self._load_api_keys()
        user_keys = []

        for key_data in api_keys:
            if key_data["user_id"] == user_id and key_data["is_active"]:
                user_keys.append(APIKey.from_dict(key_data))

        return user_keys

    def _load_api_keys(self) -> List[dict]:
        """Load API keys from file"""
        if not self.api_keys_file.exists():
            return []

        try:
            with open(self.api_keys_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load API keys: {e}")
            return []

    def _save_api_keys(self, api_keys: List[dict]):
        """Save API keys to file"""
        try:
            with open(self.api_keys_file, "w") as f:
                json.dump(api_keys, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save API keys: {e}")
            raise
