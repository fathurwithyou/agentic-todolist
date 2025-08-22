"""
Google OAuth service for handling authentication and Google Calendar access.
Provides access to both user info and Google Calendar tokens.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode
import httpx
from fastapi import HTTPException
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)


class GoogleOAuthService:
    """
    Service for handling Google OAuth2 flow with Calendar access.
    """

    def __init__(self):
        self.client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
        self.redirect_uri = "http://localhost:8000/auth/google/callback"

        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth credentials are required")

        self.scopes = [
            "openid",
            "email",
            "profile",
            "https://www.googleapis.com/auth/calendar",
        ]

        self.auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"

    def get_auth_url(self) -> str:
        """
        Generate Google OAuth authorization URL.

        Returns:
            Authorization URL for redirecting user
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "response_type": "code",
            "access_type": "offline",  # Required for refresh tokens
            "prompt": "consent",  # Force consent to get refresh token
        }

        return f"{self.auth_url}?{urlencode(params)}"

    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens.

        Args:
            code: Authorization code from Google

        Returns:
            Token response from Google
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=data)

            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.text}")
                raise HTTPException(
                    status_code=400, detail="Failed to exchange code for tokens"
                )

            return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from Google.

        Args:
            access_token: Google access token

        Returns:
            User information from Google
        """
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(self.userinfo_url, headers=headers)

            if response.status_code != 200:
                logger.error(f"Failed to get user info: {response.text}")
                raise HTTPException(
                    status_code=400, detail="Failed to get user information"
                )

            return response.json()

    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh an expired access token.

        Args:
            refresh_token: Google refresh token

        Returns:
            New token information or None if failed
        """
        try:
            # Create credentials object and refresh
            creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri=self.token_url,
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=self.scopes,
            )

            # Refresh the token
            creds.refresh(Request())

            return {
                "access_token": creds.token,
                "refresh_token": creds.refresh_token,
                "expires_in": 3600,  # Default to 1 hour
                "token_type": "Bearer",
            }

        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None

    def create_calendar_credentials(
        self, access_token: str, refresh_token: str, expires_at: datetime
    ) -> Credentials:
        """
        Create Google Credentials object for Calendar API access.

        Args:
            access_token: Google access token
            refresh_token: Google refresh token
            expires_at: Token expiration time

        Returns:
            Google Credentials object
        """
        return Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri=self.token_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=self.scopes,
            expiry=expires_at,
        )

    def is_token_expired(self, expires_at: datetime) -> bool:
        """
        Check if a token is expired.

        Args:
            expires_at: Token expiration time

        Returns:
            True if token is expired or will expire in next 5 minutes
        """
        if not expires_at:
            return True

        # Consider token expired if it expires in the next 5 minutes
        buffer_time = timedelta(minutes=5)
        return datetime.now() + buffer_time >= expires_at


# Global OAuth service instance
google_oauth_service = GoogleOAuthService()
