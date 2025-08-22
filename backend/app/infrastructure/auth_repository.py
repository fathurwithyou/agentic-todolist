"""
Authentication repository implementation.
File-based storage for development, easily replaceable with database.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from ..domains.auth.repository import AuthRepository
from ..domains.auth.models import User, UserSession

logger = logging.getLogger(__name__)


class FileAuthRepository(AuthRepository):
    """
    File-based authentication repository.
    Stores users and sessions in JSON files.
    """

    def __init__(self, data_dir: str = "data/auth"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.users_file = self.data_dir / "users.json"
        self.sessions_file = self.data_dir / "sessions.json"

    def save_user(self, user: User) -> User:
        """Save or update a user"""
        users = self._load_users()

        # Update existing or add new user
        user_dict = {
            "user_id": user.user_id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture,
            "email_verified": user.email_verified,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat(),
            "google_calendar_token": user.google_calendar_token,
            "google_calendar_refresh_token": user.google_calendar_refresh_token,
            "google_calendar_token_expiry": user.google_calendar_token_expiry.isoformat()
            if user.google_calendar_token_expiry
            else None,
        }

        # Remove existing user with same ID
        users = [u for u in users if u["user_id"] != user.user_id]
        users.append(user_dict)

        self._save_users(users)
        logger.info(f"Saved user {user.user_id}")
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        users = self._load_users()

        for user_data in users:
            if user_data["user_id"] == user_id:
                return self._dict_to_user(user_data)

        return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        users = self._load_users()

        for user_data in users:
            if user_data["email"] == email:
                return self._dict_to_user(user_data)

        return None

    def save_session(self, session: UserSession) -> UserSession:
        """Save a user session"""
        sessions = self._load_sessions()

        session_dict = {
            "session_id": session.session_id,
            "user_id": session.user.user_id,
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "expires_at": session.expires_at.isoformat(),
            "created_at": session.created_at.isoformat(),
            "is_active": session.is_active,
        }

        # Remove existing session with same ID
        sessions = [s for s in sessions if s["session_id"] != session.session_id]
        sessions.append(session_dict)

        self._save_sessions(sessions)
        logger.info(f"Saved session {session.session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID"""
        sessions = self._load_sessions()

        for session_data in sessions:
            if session_data["session_id"] == session_id and session_data["is_active"]:
                # Get the user for this session
                user = self.get_user(session_data["user_id"])
                if not user:
                    continue

                return UserSession(
                    session_id=session_data["session_id"],
                    user=user,
                    access_token=session_data["access_token"],
                    refresh_token=session_data.get("refresh_token"),
                    expires_at=datetime.fromisoformat(session_data["expires_at"]),
                    created_at=datetime.fromisoformat(session_data["created_at"]),
                    is_active=session_data["is_active"],
                )

        return None

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        sessions = self._load_sessions()

        for session in sessions:
            if session["session_id"] == session_id:
                session["is_active"] = False
                self._save_sessions(sessions)
                logger.info(f"Deleted session {session_id}")
                return True

        return False

    def delete_expired_sessions(self) -> int:
        """Delete expired sessions, return count deleted"""
        sessions = self._load_sessions()
        now = datetime.now()
        expired_count = 0

        for session in sessions:
            if session["is_active"]:
                expires_at = datetime.fromisoformat(session["expires_at"])
                if now >= expires_at:
                    session["is_active"] = False
                    expired_count += 1

        if expired_count > 0:
            self._save_sessions(sessions)
            logger.info(f"Deleted {expired_count} expired sessions")

        return expired_count

    def list_user_sessions(self, user_id: str) -> List[UserSession]:
        """List active sessions for a user"""
        sessions = self._load_sessions()
        user_sessions = []

        user = self.get_user(user_id)
        if not user:
            return []

        for session_data in sessions:
            if session_data["user_id"] == user_id and session_data["is_active"]:
                session = UserSession(
                    session_id=session_data["session_id"],
                    user=user,
                    access_token=session_data["access_token"],
                    refresh_token=session_data.get("refresh_token"),
                    expires_at=datetime.fromisoformat(session_data["expires_at"]),
                    created_at=datetime.fromisoformat(session_data["created_at"]),
                    is_active=session_data["is_active"],
                )

                if not session.is_expired:
                    user_sessions.append(session)

        return user_sessions

    def _load_users(self) -> List[dict]:
        """Load users from file"""
        if not self.users_file.exists():
            return []

        try:
            with open(self.users_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load users: {e}")
            return []

    def _save_users(self, users: List[dict]):
        """Save users to file"""
        try:
            with open(self.users_file, "w") as f:
                json.dump(users, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save users: {e}")
            raise

    def _load_sessions(self) -> List[dict]:
        """Load sessions from file"""
        if not self.sessions_file.exists():
            return []

        try:
            with open(self.sessions_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")
            return []

    def _save_sessions(self, sessions: List[dict]):
        """Save sessions to file"""
        try:
            with open(self.sessions_file, "w") as f:
                json.dump(sessions, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")
            raise

    def _dict_to_user(self, user_data: dict) -> User:
        """Convert dictionary to User object"""
        # Handle Google Calendar token expiry datetime
        google_calendar_token_expiry = None
        if user_data.get("google_calendar_token_expiry"):
            google_calendar_token_expiry = datetime.fromisoformat(
                user_data["google_calendar_token_expiry"]
            )

        return User(
            user_id=user_data["user_id"],
            email=user_data["email"],
            name=user_data["name"],
            picture=user_data.get("picture"),
            email_verified=user_data.get("email_verified", False),
            created_at=datetime.fromisoformat(user_data["created_at"]),
            last_login=datetime.fromisoformat(user_data["last_login"]),
            google_calendar_token=user_data.get("google_calendar_token"),
            google_calendar_refresh_token=user_data.get(
                "google_calendar_refresh_token"
            ),
            google_calendar_token_expiry=google_calendar_token_expiry,
        )
