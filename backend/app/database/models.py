"""
Database models for API key storage with proper hashing.
"""

import hashlib
import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

# Database directory
DATABASE_DIR = Path("database")
DATABASE_DIR.mkdir(exist_ok=True)

# Encryption key for API keys - MUST be set in environment
ENCRYPTION_KEY = os.getenv("API_KEY_ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise ValueError(
        "API_KEY_ENCRYPTION_KEY environment variable is required. "
        "Generate one with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
    )

try:
    fernet = Fernet(
        ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY
    )
except Exception as e:
    raise ValueError(f"Invalid API_KEY_ENCRYPTION_KEY format: {e}")


@dataclass
class UserAPIKey:
    """Model for storing user API keys"""

    user_id: str
    provider: str
    api_key_hash: str  # SHA-256 hash of the API key
    encrypted_api_key: str  # Encrypted API key for actual use
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "UserAPIKey":
        """Create from dictionary"""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)


class APIKeyDatabase:
    """Simple file-based database for API keys with encryption and hashing"""

    def __init__(self):
        self.db_file = DATABASE_DIR / "api_keys.json"
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Ensure the database file exists"""
        if not self.db_file.exists():
            with open(self.db_file, "w") as f:
                json.dump([], f)

    def _load_all_keys(self) -> List[UserAPIKey]:
        """Load all API keys from the database"""
        try:
            with open(self.db_file, "r") as f:
                data = json.load(f)
                return [UserAPIKey.from_dict(item) for item in data]
        except Exception as e:
            logger.error(f"Failed to load API keys from database: {e}")
            return []

    def _save_all_keys(self, keys: List[UserAPIKey]):
        """Save all API keys to the database"""
        try:
            data = [key.to_dict() for key in keys]
            with open(self.db_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save API keys to database: {e}")
            raise

    def _hash_api_key(self, api_key: str) -> str:
        """Create SHA-256 hash of API key for identification"""
        return hashlib.sha256(api_key.encode()).hexdigest()

    def _encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key for storage"""
        return fernet.encrypt(api_key.encode()).decode()

    def _decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key for use"""
        return fernet.decrypt(encrypted_key.encode()).decode()

    def save_api_key(self, user_id: str, provider: str, api_key: str) -> UserAPIKey:
        """Save or update an API key for a user"""
        keys = self._load_all_keys()

        # Remove existing key for this user/provider
        keys = [
            k for k in keys if not (k.user_id == user_id and k.provider == provider)
        ]

        # Create new key entry
        now = datetime.now()
        new_key = UserAPIKey(
            user_id=user_id,
            provider=provider,
            api_key_hash=self._hash_api_key(api_key),
            encrypted_api_key=self._encrypt_api_key(api_key),
            created_at=now,
            updated_at=now,
            is_active=True,
        )

        keys.append(new_key)
        self._save_all_keys(keys)

        logger.info(f"Saved API key for user {user_id}, provider {provider}")
        return new_key

    def get_api_key(self, user_id: str, provider: str) -> Optional[str]:
        """Get decrypted API key for a user and provider"""
        keys = self._load_all_keys()

        for key in keys:
            if key.user_id == user_id and key.provider == provider and key.is_active:
                try:
                    return self._decrypt_api_key(key.encrypted_api_key)
                except Exception as e:
                    logger.error(
                        f"Failed to decrypt API key for user {user_id}, provider {provider}: {e}"
                    )
                    return None

        return None

    def has_api_key(self, user_id: str, provider: str) -> bool:
        """Check if user has an API key for a provider"""
        keys = self._load_all_keys()

        for key in keys:
            if key.user_id == user_id and key.provider == provider and key.is_active:
                return True

        return False

    def list_user_providers(self, user_id: str) -> Dict[str, bool]:
        """List which providers have API keys for a user"""
        keys = self._load_all_keys()
        providers = ["gemini", "openai"]

        result = {}
        for provider in providers:
            result[provider] = any(
                k.user_id == user_id and k.provider == provider and k.is_active
                for k in keys
            )

        return result

    def remove_api_key(self, user_id: str, provider: str) -> bool:
        """Remove an API key for a user and provider"""
        keys = self._load_all_keys()

        # Find and mark as inactive instead of deleting (for audit trail)
        found = False
        for key in keys:
            if key.user_id == user_id and key.provider == provider and key.is_active:
                key.is_active = False
                key.updated_at = datetime.now()
                found = True
                break

        if found:
            self._save_all_keys(keys)
            logger.info(f"Removed API key for user {user_id}, provider {provider}")

        return found

    def verify_api_key_hash(self, user_id: str, provider: str, api_key: str) -> bool:
        """Verify if the provided API key matches the stored hash"""
        keys = self._load_all_keys()
        provided_hash = self._hash_api_key(api_key)

        for key in keys:
            if (
                key.user_id == user_id
                and key.provider == provider
                and key.is_active
                and key.api_key_hash == provided_hash
            ):
                return True

        return False


# Global database instance
api_key_db = APIKeyDatabase()
