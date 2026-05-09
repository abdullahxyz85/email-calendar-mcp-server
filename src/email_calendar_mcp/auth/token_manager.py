"""Secure token storage and management"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from cryptography.fernet import Fernet

from ..utils.config import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TokenManager:
    """Manages secure token storage with encryption"""

    def __init__(self):
        """Initialize token manager"""
        self.tokens_dir = settings.token_storage_path
        self.tokens_dir.mkdir(parents=True, exist_ok=True)
        self.key_path = self.tokens_dir / ".key"
        self.cipher = self._get_or_create_cipher()

    def _get_or_create_cipher(self) -> Fernet:
        """
        Get existing encryption key or create a new one

        Returns:
            Fernet cipher instance
        """
        if self.key_path.exists():
            logger.debug("Loading existing encryption key")
            with open(self.key_path, "rb") as f:
                key = f.read()
        else:
            logger.info("Creating new encryption key")
            key = Fernet.generate_key()
            self.key_path.chmod(0o600)  # Restrict access to owner only
            with open(self.key_path, "wb") as f:
                f.write(key)
            logger.info("Encryption key created and saved")

        return Fernet(key)

    def save_token(self, token_name: str, token_data: Dict[str, Any]) -> None:
        """
        Save token securely

        Args:
            token_name: Name identifier for the token
            token_data: Token data dictionary to save
        """
        try:
            # Serialize token data
            json_data = json.dumps(token_data).encode()

            # Encrypt
            encrypted_data = self.cipher.encrypt(json_data)

            # Save to file
            token_path = self.tokens_dir / f"{token_name}.enc"
            with open(token_path, "wb") as f:
                f.write(encrypted_data)

            logger.info("Token saved securely", token_name=token_name)
        except Exception as e:
            logger.error("Failed to save token", token_name=token_name, error=str(e), exc_info=True)
            raise

    def load_token(self, token_name: str) -> Optional[Dict[str, Any]]:
        """
        Load and decrypt token

        Args:
            token_name: Name identifier for the token

        Returns:
            Decrypted token data or None if not found
        """
        try:
            token_path = self.tokens_dir / f"{token_name}.enc"

            if not token_path.exists():
                logger.warning("Token file not found", token_name=token_name)
                return None

            # Read encrypted data
            with open(token_path, "rb") as f:
                encrypted_data = f.read()

            # Decrypt
            json_data = self.cipher.decrypt(encrypted_data).decode()

            # Deserialize
            token_data = json.loads(json_data)
            logger.debug("Token loaded successfully", token_name=token_name)
            return token_data
        except Exception as e:
            logger.error("Failed to load token", token_name=token_name, error=str(e), exc_info=True)
            return None

    def delete_token(self, token_name: str) -> bool:
        """
        Delete stored token

        Args:
            token_name: Name identifier for the token

        Returns:
            True if deleted, False if not found
        """
        try:
            token_path = self.tokens_dir / f"{token_name}.enc"

            if token_path.exists():
                token_path.unlink()
                logger.info("Token deleted", token_name=token_name)
                return True
            else:
                logger.warning("Token not found for deletion", token_name=token_name)
                return False
        except Exception as e:
            logger.error("Failed to delete token", token_name=token_name, error=str(e), exc_info=True)
            raise

    def list_tokens(self) -> list[str]:
        """
        List all stored tokens (without decrypting)

        Returns:
            List of token names
        """
        tokens = []
        try:
            for file in self.tokens_dir.glob("*.enc"):
                token_name = file.stem  # Remove .enc extension
                tokens.append(token_name)
            logger.debug("Tokens listed", count=len(tokens))
            return tokens
        except Exception as e:
            logger.error("Failed to list tokens", error=str(e), exc_info=True)
            return []


# Global token manager instance
_token_manager = None


def get_token_manager() -> TokenManager:
    """Get or create global token manager instance"""
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager
