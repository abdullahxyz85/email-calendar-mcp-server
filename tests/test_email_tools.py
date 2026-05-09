"""Unit tests for email tools"""

import pytest
from unittest.mock import patch, MagicMock


def test_email_tools_initialization():
    """Test EmailTools initialization"""
    from email_calendar_mcp.tools.email_tools import EmailTools

    tools = EmailTools()
    assert tools is not None


def test_email_tools_definitions():
    """Test that email tools definitions are valid"""
    from email_calendar_mcp.tools.email_tools import get_email_tools_definitions

    definitions = get_email_tools_definitions()
    assert len(definitions) > 0

    # Verify each tool has required fields
    for tool in definitions:
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool
        assert tool["inputSchema"]["type"] == "object"


def test_fetch_emails_tool_schema():
    """Test fetch_emails tool schema"""
    from email_calendar_mcp.tools.email_tools import get_email_tools_definitions

    definitions = get_email_tools_definitions()
    fetch_tool = next(t for t in definitions if t["name"] == "fetch_emails")

    assert "query" in fetch_tool["inputSchema"]["properties"]
    assert "max_results" in fetch_tool["inputSchema"]["properties"]
    assert "include_body" in fetch_tool["inputSchema"]["properties"]


def test_send_email_tool_schema():
    """Test send_email tool schema"""
    from email_calendar_mcp.tools.email_tools import get_email_tools_definitions

    definitions = get_email_tools_definitions()
    send_tool = next(t for t in definitions if t["name"] == "send_email")

    assert "to" in send_tool["inputSchema"]["properties"]
    assert "subject" in send_tool["inputSchema"]["properties"]
    assert "body" in send_tool["inputSchema"]["properties"]
    assert "to" in send_tool["inputSchema"]["required"]
