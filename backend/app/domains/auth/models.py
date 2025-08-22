"""
Authentication domain models.
Core authentication entities and value objects.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """Core user entity"""

    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    email_verified: bool = False
    created_at: datetime = None
    last_login: datetime = None
    google_calendar_token: Optional[str] = None
    google_calendar_refresh_token: Optional[str] = None
    google_calendar_token_expiry: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_login is None:
            self.last_login = datetime.now()


@dataclass
class UserSession:
    """User authentication session"""

    session_id: str
    user: User
    access_token: str
    refresh_token: Optional[str]
    expires_at: datetime
    created_at: datetime
    is_active: bool = True

    @property
    def is_expired(self) -> bool:
        return datetime.now() >= self.expires_at

    def refresh_session(self, new_token: str, expires_at: datetime):
        """Refresh the session with new token"""
        self.access_token = new_token
        self.expires_at = expires_at
        self.last_login = datetime.now()


@dataclass
class OAuthCredentials:
    """OAuth credentials for external providers"""

    provider: str
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: list[str]
