"""
Authentication domain service.
Handles all authentication business logic.
"""

import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional

from .models import User, UserSession
from .repository import AuthRepository

logger = logging.getLogger(__name__)


class AuthService:
    """
    Authentication domain service.
    Contains all authentication business logic.
    """

    def __init__(self, repository: AuthRepository, jwt_secret: str):
        self.repository = repository
        self.jwt_secret = jwt_secret

    def create_user_session(
        self,
        user: User,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_hours: int = 24,
    ) -> UserSession:
        """Create a new user session"""
        session_id = self._generate_session_id()
        expires_at = datetime.now() + timedelta(hours=expires_hours)

        session = UserSession(
            session_id=session_id,
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            created_at=datetime.now(),
        )

        self.repository.save_session(session)
        logger.info(f"Created session for user {user.user_id}")
        return session

    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get a user session by ID"""
        session = self.repository.get_session(session_id)

        if session and session.is_expired:
            self.repository.delete_session(session_id)
            logger.info(f"Expired session {session_id} cleaned up")
            return None

        return session

    def create_jwt_token(self, session: UserSession) -> str:
        """Create JWT token for session"""
        payload = {
            "session_id": session.session_id,
            "user_id": session.user.user_id,
            "email": session.user.email,
            "name": session.user.name,
            "exp": session.expires_at,
        }

        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def verify_jwt_token(self, token: str) -> Optional[UserSession]:
        """Verify JWT token and return session"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            session_id = payload.get("session_id")

            if not session_id:
                return None

            return self.get_session(session_id)

        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None

    def revoke_session(self, session_id: str) -> bool:
        """Revoke a user session"""
        success = self.repository.delete_session(session_id)
        if success:
            logger.info(f"Session {session_id} revoked")
        return success

    def clean_expired_sessions(self):
        """Clean up expired sessions"""
        expired_count = self.repository.delete_expired_sessions()
        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired sessions")

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid

        return str(uuid.uuid4())
