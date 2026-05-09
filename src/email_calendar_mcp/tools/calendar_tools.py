"""Calendar tools for MCP"""

from typing import Any

from ..services.calendar_service import get_calendar_service
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CalendarTools:
    """Calendar tool implementations"""

    @staticmethod
    def schedule_meeting(
        title: str,
        start_time: str,
        end_time: str,
        attendees: str = "",
        description: str = "",
        location: str = "",
        send_notifications: bool = True,
    ) -> dict[str, Any]:
        """
        Schedule a meeting/event

        Args:
            title: Event title
            start_time: Event start time (ISO 8601 format)
            end_time: Event end time (ISO 8601 format)
            attendees: Attendee emails (comma-separated)
            description: Event description
            location: Event location
            send_notifications: Send email notifications to attendees

        Returns:
            Dictionary with event ID or error
        """
        try:
            service = get_calendar_service()
            attendee_list = [e.strip() for e in attendees.split(",") if e.strip()] if attendees else None

            event_id = service.schedule_meeting(
                title=title,
                start_time=start_time,
                end_time=end_time,
                attendees=attendee_list,
                description=description,
                location=location,
                send_notifications=send_notifications,
            )
            return {
                "success": True,
                "event_id": event_id,
                "message": f"Meeting '{title}' scheduled successfully",
            }
        except Exception as e:
            logger.error("Error scheduling meeting", error=str(e), exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def get_calendar_availability(
        start_time: str = "",
        end_time: str = "",
    ) -> dict[str, Any]:
        """
        Get calendar availability/free time slots

        Args:
            start_time: Period start time (ISO 8601, default: now)
            end_time: Period end time (ISO 8601, default: 7 days from now)

        Returns:
            Dictionary with free time slots
        """
        try:
            service = get_calendar_service()
            availability = service.get_calendar_availability(
                start_time=start_time if start_time else None,
                end_time=end_time if end_time else None,
            )
            return {
                "success": True,
                "free_slots": availability,
                "message": f"Found {len(availability)} available time slots",
            }
        except Exception as e:
            logger.error("Error getting calendar availability", error=str(e), exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def get_events(
        start_time: str = "",
        end_time: str = "",
        max_results: int = 10,
    ) -> dict[str, Any]:
        """
        Get calendar events for a time period

        Args:
            start_time: Period start time (ISO 8601)
            end_time: Period end time (ISO 8601)
            max_results: Maximum events to return

        Returns:
            Dictionary with calendar events
        """
        try:
            service = get_calendar_service()
            events = service.get_events(
                start_time=start_time if start_time else None,
                end_time=end_time if end_time else None,
                max_results=max_results,
            )
            return {
                "success": True,
                "count": len(events),
                "events": events,
            }
        except Exception as e:
            logger.error("Error getting events", error=str(e), exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def set_reminder(
        title: str,
        due_date: str,
        description: str = "",
    ) -> dict[str, Any]:
        """
        Create a reminder/task

        Args:
            title: Reminder title
            due_date: Due date (ISO 8601)
            description: Reminder description

        Returns:
            Dictionary with reminder event or error
        """
        try:
            service = get_calendar_service()
            reminder = service.create_reminder(
                title=title,
                due_date=due_date,
                description=description,
            )
            return {
                "success": True,
                "reminder_id": reminder.get("id"),
                "message": f"Reminder '{title}' created for {due_date}",
            }
        except Exception as e:
            logger.error("Error creating reminder", error=str(e), exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def update_event(
        event_id: str,
        title: str = "",
        start_time: str = "",
        end_time: str = "",
        description: str = "",
    ) -> dict[str, Any]:
        """
        Update an existing calendar event

        Args:
            event_id: Event ID to update
            title: New event title
            start_time: New start time (ISO 8601)
            end_time: New end time (ISO 8601)
            description: New description

        Returns:
            Dictionary with success status
        """
        try:
            service = get_calendar_service()
            updates = {}
            if title:
                updates["title"] = title
            if start_time:
                updates["start_time"] = start_time
            if end_time:
                updates["end_time"] = end_time
            if description:
                updates["description"] = description

            updated_id = service.update_event(event_id, **updates)
            return {
                "success": True,
                "event_id": updated_id,
                "message": "Event updated successfully",
            }
        except Exception as e:
            logger.error("Error updating event", error=str(e), exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def delete_event(event_id: str) -> dict[str, Any]:
        """
        Delete a calendar event

        Args:
            event_id: Event ID to delete

        Returns:
            Dictionary with success status
        """
        try:
            service = get_calendar_service()
            success = service.delete_event(event_id)
            return {
                "success": success,
                "message": "Event deleted successfully" if success else "Failed to delete event",
            }
        except Exception as e:
            logger.error("Error deleting event", error=str(e), exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }


def get_calendar_tools_definitions() -> list[dict[str, Any]]:
    """
    Get MCP tool definitions for calendar operations

    Returns:
        List of tool definition dictionaries
    """
    return [
        {
            "name": "schedule_meeting",
            "description": "Schedule a meeting or calendar event",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Event title",
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Event start time (ISO 8601 format, e.g., '2024-01-15T10:00:00')",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "Event end time (ISO 8601 format)",
                    },
                    "attendees": {
                        "type": "string",
                        "description": "Attendee emails (comma-separated)",
                    },
                    "description": {
                        "type": "string",
                        "description": "Event description",
                    },
                    "location": {
                        "type": "string",
                        "description": "Event location",
                    },
                    "send_notifications": {
                        "type": "boolean",
                        "description": "Send email notifications to attendees (default: True)",
                        "default": True,
                    },
                },
                "required": ["title", "start_time", "end_time"],
            },
        },
        {
            "name": "get_calendar_availability",
            "description": "Get available time slots in the calendar",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "description": "Period start time (ISO 8601, default: now)",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "Period end time (ISO 8601, default: 7 days from now)",
                    },
                },
            },
        },
        {
            "name": "get_events",
            "description": "Get calendar events for a time period",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "description": "Period start time (ISO 8601)",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "Period end time (ISO 8601)",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum events to return (default: 10)",
                        "default": 10,
                    },
                },
            },
        },
        {
            "name": "set_reminder",
            "description": "Create a reminder or task",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Reminder title",
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date (ISO 8601 format)",
                    },
                    "description": {
                        "type": "string",
                        "description": "Reminder description",
                    },
                },
                "required": ["title", "due_date"],
            },
        },
        {
            "name": "update_event",
            "description": "Update an existing calendar event",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "Event ID to update",
                    },
                    "title": {
                        "type": "string",
                        "description": "New event title",
                    },
                    "start_time": {
                        "type": "string",
                        "description": "New start time (ISO 8601)",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "New end time (ISO 8601)",
                    },
                    "description": {
                        "type": "string",
                        "description": "New description",
                    },
                },
                "required": ["event_id"],
            },
        },
        {
            "name": "delete_event",
            "description": "Delete a calendar event",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "Event ID to delete",
                    },
                },
                "required": ["event_id"],
            },
        },
    ]
