"""
High-level LLM service with automatic fallback and provider management.
Business logic layer that orchestrates LLM operations.
"""

import logging
from typing import List, Optional

from app.providers.base import LLMProvider
from app.providers.factory import LLMFactory
from app.schemas.events import ParsedEvent
from app.config.settings import get_config

logger = logging.getLogger(__name__)


class LLMService:
    """
    High-level service for LLM operations with automatic fallback.
    """

    def __init__(self):
        self.primary_provider: Optional[LLMProvider] = None
        self.backup_provider: Optional[LLMProvider] = None
        self.initialized = False

    async def initialize(self) -> bool:
        """Initialize LLM providers based on configuration"""
        config = get_config()
        llm_config = config.llm

        logger.info(f"Initializing LLM service with provider: {llm_config.provider}")

        # Initialize primary provider
        self.primary_provider = LLMFactory.create_provider(
            provider_name=llm_config.provider,
            api_key=llm_config.api_key,
            model_name=llm_config.model_name,
        )

        if not self.primary_provider:
            logger.error(f"Failed to create primary provider: {llm_config.provider}")
            return False

        primary_success = await self.primary_provider.initialize()
        if not primary_success:
            logger.error(
                f"Failed to initialize primary provider: {llm_config.provider}"
            )

        # Initialize backup provider if configured
        if llm_config.backup_provider and llm_config.backup_api_key:
            logger.info(f"Setting up backup provider: {llm_config.backup_provider}")
            self.backup_provider = LLMFactory.create_provider(
                provider_name=llm_config.backup_provider,
                api_key=llm_config.backup_api_key,
            )

            if self.backup_provider:
                backup_success = await self.backup_provider.initialize()
                if backup_success:
                    logger.info(
                        f"Backup provider {llm_config.backup_provider} initialized successfully"
                    )
                else:
                    logger.warning(
                        f"Backup provider {llm_config.backup_provider} failed to initialize"
                    )
                    self.backup_provider = None

        self.initialized = primary_success or (self.backup_provider is not None)

        if self.initialized:
            logger.info("LLM service initialized successfully")
        else:
            logger.error("LLM service initialization failed")

        return self.initialized

    async def parse_timeline(
        self, timeline_text: str, flexible: bool = True
    ) -> List[ParsedEvent]:
        """
        Parse timeline text using available providers with automatic fallback.

        Args:
            timeline_text: Raw timeline text to parse
            flexible: Whether to use flexible prompt handling

        Returns:
            List of parsed events
        """
        if not self.initialized:
            logger.error("LLM service not initialized")
            return []

        # Try primary provider first
        if self.primary_provider and self.primary_provider.is_available():
            try:
                logger.info(
                    f"Using primary provider: {self.primary_provider.__class__.__name__}"
                )
                events = await self.primary_provider.parse_timeline(timeline_text)
                if events:
                    logger.info(f"Primary provider succeeded with {len(events)} events")
                    return events
                else:
                    logger.warning("Primary provider returned no events")
            except Exception as e:
                logger.error(f"Primary provider failed: {e}")

        # Fallback to backup provider
        if self.backup_provider and self.backup_provider.is_available():
            try:
                logger.info(
                    f"Falling back to backup provider: {self.backup_provider.__class__.__name__}"
                )
                events = await self.backup_provider.parse_timeline(timeline_text)
                if events:
                    logger.info(f"Backup provider succeeded with {len(events)} events")
                    return events
                else:
                    logger.warning("Backup provider returned no events")
            except Exception as e:
                logger.error(f"Backup provider failed: {e}")

        logger.error("All LLM providers failed")
        return []

    def get_provider_status(self) -> dict:
        """Get status of all configured providers"""
        status = {
            "initialized": self.initialized,
            "primary_provider": {
                "name": self.primary_provider.__class__.__name__
                if self.primary_provider
                else None,
                "available": self.primary_provider.is_available()
                if self.primary_provider
                else False,
                "model": self.primary_provider.model_name
                if self.primary_provider
                else None,
            },
            "backup_provider": {
                "name": self.backup_provider.__class__.__name__
                if self.backup_provider
                else None,
                "available": self.backup_provider.is_available()
                if self.backup_provider
                else False,
                "model": self.backup_provider.model_name
                if self.backup_provider
                else None,
            },
        }
        return status

    def get_available_providers(self) -> List[str]:
        """Get list of all available provider types"""
        return LLMFactory.get_available_providers()


# Global LLM service instance
llm_service = LLMService()


async def parse_timeline_text(
    timeline_text: str,
    flexible: bool = True,
    llm_provider: Optional[str] = None,
    llm_model: Optional[str] = None,
    api_key: Optional[str] = None,
    oauth_token: Optional[str] = None,
    user_id: Optional[str] = None,
) -> List[ParsedEvent]:
    """
    Convenience function to parse timeline text using the global LLM service or custom provider.

    Args:
        timeline_text: Raw timeline text to parse
        flexible: Whether to use flexible prompt handling
        llm_provider: Optional specific provider to use ('gemini', 'openai')
        llm_model: Optional specific model to use
        api_key: Optional API key provided by user
        oauth_token: Optional OAuth access token (preferred over API key)
        user_id: Optional user identifier for logging

    Returns:
        List of parsed events
    """
    from app.services.oauth_service import oauth_service
    from app.api.v1.api_keys import get_user_api_key

    # Default to gemini if no provider specified
    if not llm_provider:
        llm_provider = "gemini"

    # Try to get auth token from multiple sources in priority order:
    # 1. OAuth token (highest priority)
    # 2. Provided API key
    # 3. Stored API key from database (if user_id provided)
    auth_token = oauth_token or api_key

    if not auth_token and user_id:
        # Try to get stored API key from database
        stored_api_key = get_user_api_key(user_id, llm_provider)
        if stored_api_key:
            auth_token = stored_api_key
            logger.info(
                f"Using stored API key for user {user_id}, provider {llm_provider}"
            )
        else:
            logger.warning(
                f"No stored API key found for user {user_id}, provider {llm_provider}"
            )

    # Check if we have any authentication
    if not auth_token:
        available_methods = []
        if user_id:
            available_methods.append("save an API key in the API Keys tab")
        available_methods.append("provide an API key directly")

        methods_text = " or ".join(available_methods)
        raise ValueError(
            f"Authentication required for provider: {llm_provider}. Please {methods_text}."
        )

    # Set default model only if not provided by user
    model_name = llm_model
    if not model_name:
        if llm_provider.lower() == "gemini":
            model_name = "gemini-2.0-flash-exp"
        elif llm_provider.lower() == "openai":
            model_name = "gpt-4o-mini"
        else:
            raise ValueError(
                f"Unknown provider: {llm_provider}. Supported: 'gemini', 'openai'"
            )

    # Create temporary provider for this request using only user-provided inputs
    temp_provider = LLMFactory.create_provider(
        provider_name=llm_provider, api_key=auth_token, model_name=model_name
    )

    if not temp_provider:
        raise ValueError(f"Failed to create provider: {llm_provider}")

    # Log API usage attempt
    request_size = len(timeline_text.encode("utf-8"))
    token_hash = oauth_service._hash_token(auth_token)

    logger.info(f"Using user-provided: {llm_provider} with model: {model_name}")

    try:
        await temp_provider.initialize()
        if not temp_provider.is_available():
            oauth_service.log_api_usage(
                user_id=user_id or "anonymous",
                provider=llm_provider,
                model=model_name,
                action="parse_timeline",
                token_hash=token_hash,
                request_size=request_size,
                success=False,
                error_message="Provider not available - check authentication",
            )
            raise ValueError(
                f"Provider {llm_provider} is not available. Check your authentication."
            )

        events = await temp_provider.parse_timeline(timeline_text)

        # Log successful API usage
        response_size = (
            sum(len(str(event.__dict__).encode("utf-8")) for event in events)
            if events
            else 0
        )
        oauth_service.log_api_usage(
            user_id=user_id or "anonymous",
            provider=llm_provider,
            model=model_name,
            action="parse_timeline",
            token_hash=token_hash,
            request_size=request_size,
            response_size=response_size,
            success=True,
        )

        if not events:
            logger.warning(f"Provider {llm_provider} returned no events")

        return events

    except Exception as e:
        # Log failed API usage
        oauth_service.log_api_usage(
            user_id=user_id or "anonymous",
            provider=llm_provider,
            model=model_name,
            action="parse_timeline",
            token_hash=token_hash,
            request_size=request_size,
            success=False,
            error_message=str(e),
        )

        logger.error(f"Provider {llm_provider} failed: {e}")
        raise ValueError(f"Failed to parse timeline with {llm_provider}: {str(e)}")
