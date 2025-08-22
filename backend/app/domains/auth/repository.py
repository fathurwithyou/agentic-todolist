"""
Authentication repository interface.
Defines data access patterns for authentication domain.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from .models import User, UserSession


class AuthRepository(ABC):
    """
    Authentication repository interface.
    Defines how authentication data is stored and retrieved.
    """

    @abstractmethod
    def save_user(self, user: User) -> User:
        """Save or update a user"""
        pass

    @abstractmethod
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass

    @abstractmethod
    def save_session(self, session: UserSession) -> UserSession:
        """Save a user session"""
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID"""
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        pass

    @abstractmethod
    def delete_expired_sessions(self) -> int:
        """Delete expired sessions, return count deleted"""
        pass

    @abstractmethod
    def list_user_sessions(self, user_id: str) -> List[UserSession]:
        """List active sessions for a user"""
        pass
