"""Unit tests for calendar tools"""

import pytest
from unittest.mock import patch, MagicMock


def test_calendar_tools_initialization():
    """Test CalendarTools initialization"""
    from email_calendar_mcp.tools.calendar_tools import CalendarTools

    tools = CalendarTools()
    assert tools is not None


def test_calendar_tools_definitions():
    """Test that calendar tools definitions are valid"""
    from email_calendar_mcp.tools.calendar_tools import get_calendar_tools_definitions

    definitions = get_calendar_tools_definitions()
    assert len(definitions) > 0

    # Verify each tool has required fields
    for tool in definitions:
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool
        assert tool["inputSchema"]["type"] == "object"


def test_schedule_meeting_tool_schema():
    """Test schedule_meeting tool schema"""
    from email_calendar_mcp.tools.calendar_tools import get_calendar_tools_definitions

    definitions = get_calendar_tools_definitions()
    schedule_tool = next(t for t in definitions if t["name"] == "schedule_meeting")

    assert "title" in schedule_tool["inputSchema"]["properties"]
    assert "start_time" in schedule_tool["inputSchema"]["properties"]
    assert "end_time" in schedule_tool["inputSchema"]["properties"]


def test_get_calendar_availability_tool_schema():
    """Test get_calendar_availability tool schema"""
    from email_calendar_mcp.tools.calendar_tools import get_calendar_tools_definitions

    definitions = get_calendar_tools_definitions()
    availability_tool = next(t for t in definitions if t["name"] == "get_calendar_availability")

    assert "start_time" in availability_tool["inputSchema"]["properties"]
    assert "end_time" in availability_tool["inputSchema"]["properties"]


def test_set_reminder_tool_schema():
    """Test set_reminder tool schema"""
    from email_calendar_mcp.tools.calendar_tools import get_calendar_tools_definitions

    definitions = get_calendar_tools_definitions()
    reminder_tool = next(t for t in definitions if t["name"] == "set_reminder")

    assert "title" in reminder_tool["inputSchema"]["properties"]
    assert "due_date" in reminder_tool["inputSchema"]["properties"]
