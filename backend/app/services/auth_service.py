"""
Google SSO authentication service for user login.
Handles user authentication, session management, and profile data.
"""

import os
import jwt
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from google.oauth2 import id_token
import google.auth.transport.requests

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """User profile from Google SSO"""

    user_id: str
    email: str
    name: str
    picture: Optional[str]
    email_verified: bool
    created_at: datetime
    last_login: datetime


@dataclass
class UserSession:
    """User session data"""

    session_id: str
    user_profile: UserProfile
    access_token: str
    refresh_token: Optional[str]
    expires_at: datetime
    created_at: datetime


class GoogleSSOService:
    """
    Service for handling Google SSO authentication and user sessions.
    """

    def __init__(self):
        self.sessions: Dict[str, UserSession] = {}
        self.users: Dict[str, UserProfile] = {}
        self.client_id = os.getenv("GOOGLE_SSO_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_SSO_CLIENT_SECRET")
        self.jwt_secret = os.getenv(
            "JWT_SECRET_KEY", "your-secret-key-change-in-production"
        )

    def get_google_sso_url(self, redirect_uri: str, state: Optional[str] = None) -> str:
        """
        Generate Google SSO authorization URL.

        Args:
            redirect_uri: Callback URL after authentication
            state: Optional state parameter for CSRF protection

        Returns:
            Google SSO authorization URL
        """
        from urllib.parse import urlencode

        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": "openid email profile",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
        }

        if state:
            params["state"] = state

        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        return f"{base_url}?{urlencode(params)}"

    async def exchange_code_for_tokens(
        self, authorization_code: str, redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access and ID tokens.

        Args:
            authorization_code: Code from Google SSO callback
            redirect_uri: Original redirect URI

        Returns:
            Token response from Google
        """
        import httpx

        token_url = "https://oauth2.googleapis.com/token"

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": authorization_code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)

            if response.status_code != 200:
                raise ValueError(f"Token exchange failed: {response.text}")

            return response.json()

    def verify_google_token(self, id_token_str: str) -> Dict[str, Any]:
        """
        Verify Google ID token and extract user info.

        Args:
            id_token_str: ID token from Google

        Returns:
            Verified token payload with user info
        """
        try:
            # Verify the token
            request = google.auth.transport.requests.Request()
            id_info = id_token.verify_oauth2_token(
                id_token_str, request, self.client_id
            )

            # Verify the issuer
            if id_info["iss"] not in [
                "accounts.google.com",
                "https://accounts.google.com",
            ]:
                raise ValueError("Wrong issuer.")

            return id_info

        except ValueError as e:
            logger.error(f"Token verification failed: {e}")
            raise ValueError(f"Invalid token: {str(e)}")

    async def authenticate_user(
        self, authorization_code: str, redirect_uri: str
    ) -> UserSession:
        """
        Authenticate user with Google SSO and create session.

        Args:
            authorization_code: Authorization code from Google
            redirect_uri: Original redirect URI

        Returns:
            User session with profile data
        """
        # Exchange code for tokens
        tokens = await self.exchange_code_for_tokens(authorization_code, redirect_uri)

        # Verify ID token and get user info
        id_info = self.verify_google_token(tokens["id_token"])

        # Create or update user profile
        user_profile = UserProfile(
            user_id=id_info["sub"],
            email=id_info["email"],
            name=id_info.get("name", ""),
            picture=id_info.get("picture"),
            email_verified=id_info.get("email_verified", False),
            created_at=self.users.get(
                id_info["sub"],
                UserProfile(
                    user_id=id_info["sub"],
                    email="",
                    name="",
                    picture=None,
                    email_verified=False,
                    created_at=datetime.now(),
                    last_login=datetime.now(),
                ),
            ).created_at
            if id_info["sub"] in self.users
            else datetime.now(),
            last_login=datetime.now(),
        )

        # Store user profile
        self.users[user_profile.user_id] = user_profile

        # Create session
        session_id = self._generate_session_id()
        expires_at = datetime.now() + timedelta(hours=24)  # 24 hour session

        session = UserSession(
            session_id=session_id,
            user_profile=user_profile,
            access_token=tokens["access_token"],
            refresh_token=tokens.get("refresh_token"),
            expires_at=expires_at,
            created_at=datetime.now(),
        )

        # Store session
        self.sessions[session_id] = session

        logger.info(f"User authenticated successfully: {user_profile.email}")

        return session

    def create_jwt_token(self, session: UserSession) -> str:
        """
        Create JWT token for session.

        Args:
            session: User session

        Returns:
            JWT token string
        """
        payload = {
            "session_id": session.session_id,
            "user_id": session.user_profile.user_id,
            "email": session.user_profile.email,
            "name": session.user_profile.name,
            "exp": session.expires_at.timestamp(),
            "iat": datetime.now().timestamp(),
        }

        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def verify_jwt_token(self, token: str) -> Optional[UserSession]:
        """
        Verify JWT token and get session.

        Args:
            token: JWT token string

        Returns:
            User session if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            session_id = payload["session_id"]

            session = self.sessions.get(session_id)
            if not session:
                return None

            # Check if session is expired
            if datetime.now() >= session.expires_at:
                del self.sessions[session_id]
                return None

            return session

        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None

    def get_user_session(self, session_id: str) -> Optional[UserSession]:
        """
        Get user session by session ID.

        Args:
            session_id: Session identifier

        Returns:
            User session if exists and valid
        """
        session = self.sessions.get(session_id)
        if not session:
            return None

        # Check if session is expired
        if datetime.now() >= session.expires_at:
            del self.sessions[session_id]
            return None

        return session

    def revoke_session(self, session_id: str) -> bool:
        """
        Revoke user session.

        Args:
            session_id: Session identifier

        Returns:
            True if session was revoked, False if not found
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            del self.sessions[session_id]
            logger.info(f"Session revoked for user: {session.user_profile.email}")
            return True
        return False

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Get user profile by user ID.

        Args:
            user_id: User identifier

        Returns:
            User profile if exists
        """
        return self.users.get(user_id)

    def list_active_sessions(self) -> list[UserSession]:
        """
        Get list of all active sessions.

        Returns:
            List of active user sessions
        """
        now = datetime.now()
        active_sessions = []
        expired_sessions = []

        for session_id, session in self.sessions.items():
            if session.expires_at > now:
                active_sessions.append(session)
            else:
                expired_sessions.append(session_id)

        # Clean up expired sessions
        for session_id in expired_sessions:
            del self.sessions[session_id]

        return active_sessions

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid

        return str(uuid.uuid4())

    async def refresh_user_token(self, session: UserSession) -> Optional[UserSession]:
        """
        Refresh user's access token using refresh token.

        Args:
            session: Current user session

        Returns:
            Updated session with new tokens, or None if refresh failed
        """
        if not session.refresh_token:
            return None

        import httpx

        token_url = "https://oauth2.googleapis.com/token"

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": session.refresh_token,
            "grant_type": "refresh_token",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(token_url, data=data)

                if response.status_code != 200:
                    logger.error(f"Token refresh failed: {response.text}")
                    return None

                tokens = response.json()

                # Update session with new token
                session.access_token = tokens["access_token"]
                session.expires_at = datetime.now() + timedelta(hours=24)

                # Update stored session
                self.sessions[session.session_id] = session

                logger.info(f"Token refreshed for user: {session.user_profile.email}")
                return session

        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return None


# Global auth service instance
auth_service = GoogleSSOService()
