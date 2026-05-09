"""Unit tests for token manager"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def test_token_manager_initialization():
    """Test TokenManager initialization"""
    from email_calendar_mcp.auth.token_manager import TokenManager

    manager = TokenManager()
    assert manager.tokens_dir.exists()
    assert manager.cipher is not None


def test_token_save_and_load():
    """Test saving and loading tokens"""
    from email_calendar_mcp.auth.token_manager import TokenManager

    manager = TokenManager()
    test_token = {"access_token": "test123", "refresh_token": "refresh123"}

    # Save token
    manager.save_token("test_token", test_token)

    # Load token
    loaded_token = manager.load_token("test_token")
    assert loaded_token == test_token

    # Cleanup
    manager.delete_token("test_token")


def test_token_encryption():
    """Test that tokens are properly encrypted"""
    from email_calendar_mcp.auth.token_manager import TokenManager

    manager = TokenManager()
    test_token = {"access_token": "secret123"}

    manager.save_token("test_enc", test_token)

    # Verify file is encrypted (not plain text)
    token_path = manager.tokens_dir / "test_enc.enc"
    with open(token_path, "rb") as f:
        content = f.read()

    # Encrypted content should not contain the plaintext
    assert b"secret123" not in content

    # Cleanup
    manager.delete_token("test_enc")


def test_token_delete():
    """Test token deletion"""
    from email_calendar_mcp.auth.token_manager import TokenManager

    manager = TokenManager()
    test_token = {"access_token": "test123"}

    manager.save_token("test_delete", test_token)
    assert manager.delete_token("test_delete") is True
    assert manager.delete_token("test_delete") is False  # Already deleted


def test_list_tokens():
    """Test listing tokens"""
    from email_calendar_mcp.auth.token_manager import TokenManager

    manager = TokenManager()

    # Create a few test tokens
    manager.save_token("token1", {"data": "test1"})
    manager.save_token("token2", {"data": "test2"})

    tokens = manager.list_tokens()
    assert "token1" in tokens
    assert "token2" in tokens

    # Cleanup
    manager.delete_token("token1")
    manager.delete_token("token2")
