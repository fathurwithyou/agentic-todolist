"""
Clean authentication API endpoints.
Uses domain services for business logic.
"""

import os
import logging
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from ..domains.auth.service import AuthService
from ..domains.auth.models import User
from ..infrastructure.auth_repository import FileAuthRepository
from ..services.google_oauth_service import google_oauth_service

logger = logging.getLogger(__name__)

# Initialize dependencies
auth_repository = FileAuthRepository()
jwt_secret = os.getenv("JWT_SECRET")
if not jwt_secret:
    raise ValueError("JWT_SECRET environment variable is required")

auth_service = AuthService(auth_repository, jwt_secret)

# Google OAuth service is initialized in the import

router = APIRouter(prefix="/auth", tags=["authentication"])


class UserProfileResponse(BaseModel):
    """User profile response"""

    user_id: str
    email: str
    name: str
    picture: Optional[str] = None


def get_current_user(request: Request):
    """Dependency to get current authenticated user"""
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid authorization header"
        )

    token = auth_header.split(" ")[1]
    session = auth_service.verify_jwt_token(token)

    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return session


@router.get("/google")
async def google_login():
    """Initiate Google OAuth login"""
    try:
        auth_url = google_oauth_service.get_auth_url()
        return RedirectResponse(url=auth_url)
    except Exception as e:
        logger.error(f"Failed to get Google login redirect: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate Google login")


@router.get("/google/callback")
async def google_callback(request: Request):
    """Handle Google OAuth callback"""
    try:
        # Get authorization code from request
        code = request.query_params.get("code")
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code not found")

        # Exchange code for tokens
        token_response = await google_oauth_service.exchange_code_for_tokens(code)
        access_token = token_response["access_token"]
        refresh_token = token_response.get("refresh_token")
        expires_in = token_response.get("expires_in", 3600)

        # Calculate token expiry
        token_expiry = datetime.now() + timedelta(seconds=expires_in)

        # Get user info from Google
        user_info = await google_oauth_service.get_user_info(access_token)

        # Create or update user with calendar tokens
        user = User(
            user_id=user_info["id"],
            email=user_info["email"],
            name=user_info.get("name", user_info["email"]),
            picture=user_info.get("picture"),
            email_verified=user_info.get("verified_email", True),
            google_calendar_token=access_token,
            google_calendar_refresh_token=refresh_token,
            google_calendar_token_expiry=token_expiry,
        )

        # Save user to repository
        auth_repository.save_user(user)

        # Create session
        session = auth_service.create_user_session(
            user=user, access_token=access_token, expires_hours=24
        )

        # Generate JWT token
        jwt_token = auth_service.create_jwt_token(session)

        # Redirect to frontend with token
        frontend_url = f"http://localhost:8000/?token={jwt_token}"
        return RedirectResponse(url=frontend_url)

    except Exception as e:
        logger.error(f"Google callback failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Authentication callback failed: {str(e)}"
        )


@router.get("/verify")
async def verify_token(token: str):
    """Verify JWT token and return user info"""
    session = auth_service.verify_jwt_token(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return {
        "valid": True,
        "user": {
            "user_id": session.user.user_id,
            "email": session.user.email,
            "name": session.user.name,
            "picture": session.user.picture,
        },
    }


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfileResponse(
        user_id=current_user.user.user_id,
        email=current_user.user.email,
        name=current_user.user.name,
        picture=current_user.user.picture,
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user"""
    success = auth_service.revoke_session(current_user.session_id)
    return {"success": success, "message": "Logged out successfully"}


@router.get("/calendar-status")
async def get_calendar_status(current_user: User = Depends(get_current_user)):
    """Check if user has Google Calendar access"""
    user = current_user.user
    has_calendar_access = (
        user.google_calendar_token is not None
        and user.google_calendar_refresh_token is not None
    )

    token_expired = False
    if has_calendar_access and user.google_calendar_token_expiry:
        from ..services.google_oauth_service import google_oauth_service

        token_expired = google_oauth_service.is_token_expired(
            user.google_calendar_token_expiry
        )

    return {
        "has_calendar_access": has_calendar_access,
        "token_expired": token_expired,
        "needs_reauth": not has_calendar_access or token_expired,
        "message": "Re-authenticate with Google to access Calendar features"
        if not has_calendar_access or token_expired
        else "Calendar access available",
    }
