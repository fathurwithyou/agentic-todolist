"""
LLM domain models.
API keys, providers, and LLM-related entities.
"""

import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List
from enum import Enum


class ProviderType(Enum):
    """Supported LLM providers"""

    GEMINI = "gemini"
    OPENAI = "openai"


@dataclass
class APIKey:
    """Encrypted API key storage"""

    user_id: str
    provider: ProviderType
    api_key_hash: str  # SHA-256 hash for identification
    encrypted_api_key: str  # Encrypted for storage
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    @classmethod
    def create_hash(cls, api_key: str) -> str:
        """Create SHA-256 hash of API key"""
        return hashlib.sha256(api_key.encode()).hexdigest()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data["provider"] = self.provider.value
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "APIKey":
        """Create from dictionary"""
        data["provider"] = ProviderType(data["provider"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)


@dataclass
class LLMProvider:
    """LLM provider configuration"""

    name: ProviderType
    display_name: str
    models: List[str]
    default_model: str
    api_base_url: Optional[str] = None

    @property
    def is_supported(self) -> bool:
        """Check if provider is supported"""
        return len(self.models) > 0


@dataclass
class LLMRequest:
    """Request to LLM service"""

    user_id: str
    provider: ProviderType
    model: str
    prompt: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


@dataclass
class LLMResponse:
    """Response from LLM service"""

    provider: ProviderType
    model: str
    content: str
    usage: dict
    created_at: datetime
