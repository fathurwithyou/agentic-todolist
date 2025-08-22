"""
API key encryption service.
Handles encryption/decryption of sensitive API keys.
"""

import os
from cryptography.fernet import Fernet


class APIKeyEncryption:
    """
    Service for encrypting and decrypting API keys.
    Uses Fernet symmetric encryption.
    """

    def __init__(self, encryption_key: str = None):
        if encryption_key is None:
            encryption_key = os.getenv("API_KEY_ENCRYPTION_KEY")

        if not encryption_key:
            raise ValueError(
                "API_KEY_ENCRYPTION_KEY environment variable is required. "
                "Generate one with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            )

        try:
            self.fernet = Fernet(
                encryption_key.encode()
                if isinstance(encryption_key, str)
                else encryption_key
            )
        except Exception as e:
            raise ValueError(f"Invalid API_KEY_ENCRYPTION_KEY format: {e}")

    def encrypt(self, api_key: str) -> str:
        """Encrypt API key for storage"""
        return self.fernet.encrypt(api_key.encode()).decode()

    def decrypt(self, encrypted_key: str) -> str:
        """Decrypt API key for use"""
        return self.fernet.decrypt(encrypted_key.encode()).decode()
