"""OAuth 2.0 authentication flow handler"""

import json
import pickle
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from ..utils.config import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class GoogleOAuthManager:
    """Manages Google OAuth 2.0 authentication flow and token refresh"""

    # Google OAuth scopes required
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events",
    ]

    def __init__(self):
        """Initialize OAuth manager"""
        self.token_path = settings.token_storage_path / "google_token.pickle"
        self.credentials_path = settings.credentials_storage_path / "google_credentials.json"
        self.credentials: Optional[Credentials] = None

    def get_credentials(self) -> Credentials:
        """
        Get valid Google credentials, refreshing if necessary

        Returns:
            Valid Credentials object

        Raises:
            ValueError: If credentials cannot be obtained
        """
        # Try to load existing token
        if self.token_path.exists():
            logger.info("Loading existing token from cache", token_path=str(self.token_path))
            self.credentials = self._load_token()

            if self.credentials and self.credentials.valid:
                return self.credentials

            # Token expired, try to refresh
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                logger.info("Token expired, refreshing...")
                self._refresh_token()
                return self.credentials

        # No valid token, perform OAuth flow
        logger.info("Initiating OAuth 2.0 flow")
        flow = self._create_oauth_flow()
        self.credentials = flow.run_local_server(port=8080)

        # Save token for future use
        self._save_token(self.credentials)
        logger.info("Token saved successfully", token_path=str(self.token_path))

        return self.credentials

    def _create_oauth_flow(self) -> InstalledAppFlow:
        """
        Create OAuth flow from credentials file

        Returns:
            InstalledAppFlow object

        Raises:
            FileNotFoundError: If credentials file not found
        """
        if not self.credentials_path.exists():
            raise FileNotFoundError(
                f"Google credentials file not found at {self.credentials_path}\n"
                "Please download your OAuth 2.0 credentials from Google Cloud Console\n"
                "and place it at: config/google_credentials.json"
            )

        logger.debug("Creating OAuth flow from credentials", path=str(self.credentials_path))
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_path, self.SCOPES
        )
        return flow

    def _save_token(self, credentials: Credentials) -> None:
        """
        Save credentials token to file

        Args:
            credentials: Credentials object to save
        """
        try:
            with open(self.token_path, "wb") as token_file:
                pickle.dump(credentials, token_file)
            logger.info("Credentials token saved", path=str(self.token_path))
        except Exception as e:
            logger.error("Failed to save token", error=str(e), exc_info=True)
            raise

    def _load_token(self) -> Optional[Credentials]:
        """
        Load credentials token from file

        Returns:
            Credentials object or None if load fails
        """
        try:
            with open(self.token_path, "rb") as token_file:
                credentials = pickle.load(token_file)
            logger.debug("Token loaded successfully", path=str(self.token_path))
            return credentials
        except Exception as e:
            logger.error("Failed to load token", error=str(e), exc_info=True)
            return None

    def _refresh_token(self) -> None:
        """Refresh expired token"""
        try:
            if self.credentials is None:
                raise ValueError("No credentials to refresh")

            request = Request()
            self.credentials.refresh(request)
            self._save_token(self.credentials)
            logger.info("Token refreshed successfully")
        except Exception as e:
            logger.error("Failed to refresh token", error=str(e), exc_info=True)
            raise

    def revoke_credentials(self) -> None:
        """Revoke credentials and delete token file"""
        try:
            if self.credentials and hasattr(self.credentials, 'revoke'):
                request = Request()
                self.credentials.revoke(request)
                logger.info("Credentials revoked")

            if self.token_path.exists():
                self.token_path.unlink()
                logger.info("Token file deleted", path=str(self.token_path))
        except Exception as e:
            logger.error("Failed to revoke credentials", error=str(e), exc_info=True)
            raise


# Global OAuth manager instance
_oauth_manager = None


def get_oauth_manager() -> GoogleOAuthManager:
    """Get or create global OAuth manager instance"""
    global _oauth_manager
    if _oauth_manager is None:
        _oauth_manager = GoogleOAuthManager()
    return _oauth_manager
