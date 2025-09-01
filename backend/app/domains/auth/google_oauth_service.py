"""
Google OAuth service for authentication.
Moved from app/services to domains for clean architecture.
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class GoogleOAuthService:
    """Service for Google OAuth operations"""
    
    def __init__(self):
        self.creds = None
        self.client_id = os.getenv("GOOGLE_SSO_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_SSO_CLIENT_SECRET")
        self.redirect_uri = "http://localhost:8000/auth/google/callback"
    
    def get_auth_url(self) -> str:
        """Get Google OAuth authorization URL"""
        try:
            from google_auth_oauthlib.flow import Flow
            
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri],
                    }
                },
                scopes=[
                    "https://www.googleapis.com/auth/userinfo.email",
                    "https://www.googleapis.com/auth/userinfo.profile", 
                    "openid",
                    "https://www.googleapis.com/auth/calendar"
                ]
            )
            flow.redirect_uri = self.redirect_uri
            
            auth_url, _ = flow.authorization_url(prompt="consent")
            return auth_url
            
        except Exception as e:
            logger.error(f"Failed to generate auth URL: {e}")
            raise
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        try:
            from google_auth_oauthlib.flow import Flow
            import asyncio
            
            def _exchange_code():
                flow = Flow.from_client_config(
                    {
                        "web": {
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": [self.redirect_uri],
                        }
                    },
                    scopes=[
                        "https://www.googleapis.com/auth/userinfo.email",
                        "https://www.googleapis.com/auth/userinfo.profile",
                        "openid", 
                        "https://www.googleapis.com/auth/calendar"
                    ]
                )
                flow.redirect_uri = self.redirect_uri
                
                flow.fetch_token(code=code)
                return flow.credentials
            
            credentials = await asyncio.to_thread(_exchange_code)
            
            expires_in = 3600  # Default 1 hour
            if credentials.expiry:
                expires_in = int((credentials.expiry - datetime.now()).total_seconds())
            
            return {
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "expires_in": expires_in,
                "expires_at": credentials.expiry,
            }
            
        except Exception as e:
            logger.error(f"Failed to exchange code for tokens: {e}")
            raise
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user info from Google"""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            raise
    
    def is_token_expired(self, expires_at: datetime) -> bool:
        """Check if token is expired"""
        return datetime.now() >= expires_at
    
    def authenticate(self) -> bool:
        """Authenticate with Google services"""
        try:
            logger.info("Google OAuth service initialized")
            return True
        except Exception as e:
            logger.error(f"Google OAuth authentication failed: {e}")
            return False


# Global instance
google_oauth_service = GoogleOAuthService()