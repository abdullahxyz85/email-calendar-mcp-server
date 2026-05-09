"""Configuration management module"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Google OAuth
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    google_redirect_uri: str = os.getenv(
        "GOOGLE_REDIRECT_URI", "http://localhost:8080/callback"
    )

    # Microsoft OAuth (optional)
    microsoft_client_id: Optional[str] = os.getenv("MICROSOFT_CLIENT_ID")
    microsoft_client_secret: Optional[str] = os.getenv("MICROSOFT_CLIENT_SECRET")

    # Email Provider
    email_provider: str = os.getenv("EMAIL_PROVIDER", "gmail")

    # Paths
    token_storage_path: Path = Path(os.getenv("TOKEN_STORAGE_PATH", "./tokens"))
    credentials_storage_path: Path = Path(
        os.getenv("CREDENTIALS_STORAGE_PATH", "./credentials")
    )

    # Server Configuration
    server_host: str = os.getenv("SERVER_HOST", "localhost")
    server_port: int = int(os.getenv("SERVER_PORT", 8000))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **data):
        super().__init__(**data)
        # Create required directories
        self.token_storage_path.mkdir(parents=True, exist_ok=True)
        self.credentials_storage_path.mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    """Get application settings"""
    # Load .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file)

    return Settings()


# Global settings instance
settings = get_settings()
