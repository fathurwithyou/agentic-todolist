"""
Configuration management for the application.
Centralized settings with environment variable support.
"""

import os
from typing import Optional, Dict
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class GoogleConfig:
    """Google Calendar API configuration"""

    service_account_path: Optional[str]
    credentials_path: Optional[str]
    calendar_id: str


@dataclass
class LLMConfig:
    """LLM provider configuration"""

    provider: str  # "gemini", "openai", etc.
    api_key: Optional[str]
    model_name: str
    backup_provider: Optional[str] = None
    backup_api_key: Optional[str] = None


@dataclass
class ServerConfig:
    """FastAPI server configuration"""

    host: str
    port: int
    reload: bool


@dataclass
class EmailMappingConfig:
    """Email mapping configuration for attendees"""

    mappings: Dict[str, str]


class Config:
    """Main configuration class that loads all settings"""

    def __init__(self, env_file: Optional[str] = None):
        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        self.google = self._load_google_config()
        self.llm = self._load_llm_config()
        self.server = self._load_server_config()
        self.email_mapping = self._load_email_mapping_config()

    def _load_google_config(self) -> GoogleConfig:
        """Load Google Calendar API configuration"""
        service_account_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH")
        credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
        calendar_id = os.getenv("CALENDAR_ID", "primary")

        # Validate that at least one authentication method is configured
        if not service_account_path and not credentials_path:
            print("Warning: No Google Calendar authentication configured")

        return GoogleConfig(
            service_account_path=service_account_path,
            credentials_path=credentials_path,
            calendar_id=calendar_id,
        )

    def _load_llm_config(self) -> LLMConfig:
        """Load LLM provider configuration"""
        provider = os.getenv("LLM_PROVIDER", "gemini").lower()

        # Get API keys for different providers
        api_key = None
        if provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            default_model = "gemini-2.0-flash-exp"
        elif provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            default_model = "gpt-4o-mini"
        else:
            # For custom providers, try generic keys
            api_key = os.getenv("LLM_API_KEY")
            default_model = "default"

        model_name = os.getenv("LLM_MODEL", default_model)

        # Backup provider configuration
        backup_provider = os.getenv("LLM_BACKUP_PROVIDER")
        backup_api_key = None
        if backup_provider:
            if backup_provider.lower() == "gemini":
                backup_api_key = os.getenv("GEMINI_API_KEY")
            elif backup_provider.lower() == "openai":
                backup_api_key = os.getenv("OPENAI_API_KEY")

        return LLMConfig(
            provider=provider,
            api_key=api_key,
            model_name=model_name,
            backup_provider=backup_provider,
            backup_api_key=backup_api_key,
        )

    def _load_server_config(self) -> ServerConfig:
        """Load FastAPI server configuration"""
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        reload = os.getenv("RELOAD", "true").lower() == "true"

        return ServerConfig(host=host, port=port, reload=reload)

    def _load_email_mapping_config(self) -> EmailMappingConfig:
        """Load email mapping configuration for attendees"""
        mappings = {}

        # Load mappings from environment variables only
        # Format: ATTENDEE_<NAME>_EMAIL=email@domain.com
        for key, value in os.environ.items():
            if key.startswith("ATTENDEE_") and key.endswith("_EMAIL"):
                name = key[9:-6].lower()  # Remove ATTENDEE_ and _EMAIL
                if value:
                    mappings[name] = value

        return EmailMappingConfig(mappings=mappings)

    def get_email_for_attendee(self, name: str) -> str:
        """Get email address for an attendee name"""
        name_lower = name.lower().strip()
        return self.email_mapping.mappings.get(name_lower, f"{name_lower}@domain.com")

    def validate_config(self) -> bool:
        """Validate the configuration"""
        errors = []

        # Check Google Calendar configuration
        if not self.google.service_account_path and not self.google.credentials_path:
            errors.append("No Google Calendar authentication configured")

        # Check if files exist
        if self.google.service_account_path and not os.path.exists(
            self.google.service_account_path
        ):
            errors.append(
                f"Service account file not found: {self.google.service_account_path}"
            )

        if self.google.credentials_path and not os.path.exists(
            self.google.credentials_path
        ):
            errors.append(f"Credentials file not found: {self.google.credentials_path}")

        # Check server configuration
        if self.server.port < 1 or self.server.port > 65535:
            errors.append(f"Invalid port number: {self.server.port}")

        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False

        return True


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance"""
    return config


def reload_config(env_file: Optional[str] = None) -> Config:
    """Reload configuration from environment variables"""
    global config
    config = Config(env_file)
    return config
