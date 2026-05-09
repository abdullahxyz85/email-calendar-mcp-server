"""Test fixtures and configuration"""

import pytest


@pytest.fixture
def mock_credentials():
    """Mock Google credentials for testing"""
    from unittest.mock import MagicMock

    credentials = MagicMock()
    credentials.valid = True
    credentials.expired = False
    credentials.refresh_token = None
    return credentials


@pytest.fixture
def mock_oauth_manager(mock_credentials):
    """Mock OAuth manager"""
    from unittest.mock import MagicMock

    manager = MagicMock()
    manager.get_credentials.return_value = mock_credentials
    return manager
