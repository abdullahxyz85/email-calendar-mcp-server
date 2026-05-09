"""Calendar service for Google Calendar operations"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..auth.oauth import get_oauth_manager
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CalendarService:
    """Service for Google Calendar operations"""

    def __init__(self):
        """Initialize calendar service"""
        self.oauth_manager = get_oauth_manager()
        self.service = None
        self._initialize_service()

    def _initialize_service(self) -> None:
        """Initialize Google Calendar API service"""
        try:
            credentials = self.oauth_manager.get_credentials()
            self.service = build("calendar", "v3", credentials=credentials)
            logger.info("Google Calendar service initialized")
        except Exception as e:
            logger.error("Failed to initialize Calendar service", error=str(e), exc_info=True)
            raise

    def list_calendars(self) -> List[Dict[str, Any]]:
        """
        List all calendars

        Returns:
            List of calendar dictionaries
        """
        try:
            logger.info("Listing calendars")
            results = self.service.calendarList().list().execute()
            calendars = results.get("items", [])
            logger.info("Calendars retrieved", count=len(calendars))
            return calendars
        except HttpError as e:
            logger.error("Failed to list calendars", error=str(e), exc_info=True)
            raise

    def get_calendar_availability(
        self,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        calendar_id: str = "primary",
    ) -> List[Dict[str, Any]]:
        """
        Get calendar availability/free time

        Args:
            start_time: Start time (ISO 8601 format, default: now)
            end_time: End time (ISO 8601 format, default: 7 days from now)
            calendar_id: Calendar ID to check

        Returns:
            List of availability slots
        """
        try:
            if not start_time:
                start_time = datetime.utcnow().isoformat() + "Z"
            if not end_time:
                end_time = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"

            logger.info(
                "Getting calendar availability",
                start_time=start_time,
                end_time=end_time,
                calendar_id=calendar_id,
            )

            # Get all events for the time period
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy="startTime",
            ).execute()

            events = events_result.get("items", [])
            logger.info("Calendar events retrieved", count=len(events))

            # Calculate free slots
            free_slots = self._calculate_free_slots(start_time, end_time, events)
            return free_slots

        except HttpError as e:
            logger.error("Failed to get calendar availability", error=str(e), exc_info=True)
            raise

    def _calculate_free_slots(
        self,
        start_time: str,
        end_time: str,
        events: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Calculate free time slots from busy events

        Args:
            start_time: Period start time
            end_time: Period end time
            events: List of booked events

        Returns:
            List of free slots
        """
        try:
            start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))

            free_slots = []
            current = start

            for event in events:
                event_start = datetime.fromisoformat(
                    event.get("start", {}).get("dateTime", "").replace("Z", "+00:00")
                )
                event_end = datetime.fromisoformat(
                    event.get("end", {}).get("dateTime", "").replace("Z", "+00:00")
                )

                # If there's a gap between current time and event start
                if current < event_start:
                    free_slots.append({
                        "start": current.isoformat(),
                        "end": event_start.isoformat(),
                        "duration_minutes": int((event_start - current).total_seconds() / 60),
                    })

                current = max(current, event_end)

            # Add final free slot if any
            if current < end:
                free_slots.append({
                    "start": current.isoformat(),
                    "end": end.isoformat(),
                    "duration_minutes": int((end - current).total_seconds() / 60),
                })

            logger.debug("Free slots calculated", count=len(free_slots))
            return free_slots
        except Exception as e:
            logger.error("Failed to calculate free slots", error=str(e), exc_info=True)
            return []

    def schedule_meeting(
        self,
        title: str,
        start_time: str,
        end_time: str,
        attendees: Optional[List[str]] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        calendar_id: str = "primary",
        send_notifications: bool = True,
    ) -> str:
        """
        Schedule a meeting/event

        Args:
            title: Event title
            start_time: Event start time (ISO 8601)
            end_time: Event end time (ISO 8601)
            attendees: List of attendee email addresses
            description: Event description
            location: Event location
            calendar_id: Calendar ID to add event to
            send_notifications: Whether to send notifications to attendees

        Returns:
            Event ID
        """
        try:
            logger.info("Scheduling meeting", title=title, start_time=start_time)

            event = {
                "summary": title,
                "start": {"dateTime": start_time},
                "end": {"dateTime": end_time},
                "description": description or "",
                "location": location or "",
            }

            # Add attendees
            if attendees:
                event["attendees"] = [{"email": email} for email in attendees]

            # Create event
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event,
                sendNotifications=send_notifications,
            ).execute()

            logger.info("Meeting scheduled successfully", event_id=created_event["id"])
            return created_event["id"]

        except HttpError as e:
            logger.error("Failed to schedule meeting", error=str(e), exc_info=True)
            raise

    def get_events(
        self,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        calendar_id: str = "primary",
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get calendar events for a time period

        Args:
            start_time: Start time (ISO 8601)
            end_time: End time (ISO 8601)
            calendar_id: Calendar ID
            max_results: Maximum events to return

        Returns:
            List of event dictionaries
        """
        try:
            if not start_time:
                start_time = datetime.utcnow().isoformat() + "Z"
            if not end_time:
                end_time = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"

            logger.info("Getting events", start_time=start_time, calendar_id=calendar_id)

            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start_time,
                timeMax=end_time,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            ).execute()

            events = events_result.get("items", [])
            logger.info("Events retrieved", count=len(events))
            return events

        except HttpError as e:
            logger.error("Failed to get events", error=str(e), exc_info=True)
            raise

    def update_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
        **updates,
    ) -> str:
        """
        Update an existing event

        Args:
            event_id: Event ID to update
            calendar_id: Calendar ID
            **updates: Fields to update (title, start_time, end_time, etc.)

        Returns:
            Updated event ID
        """
        try:
            logger.info("Updating event", event_id=event_id)

            # Get existing event
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id,
            ).execute()

            # Update fields
            if "title" in updates:
                event["summary"] = updates["title"]
            if "description" in updates:
                event["description"] = updates["description"]
            if "start_time" in updates:
                event["start"]["dateTime"] = updates["start_time"]
            if "end_time" in updates:
                event["end"]["dateTime"] = updates["end_time"]

            # Save changes
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event,
            ).execute()

            logger.info("Event updated successfully", event_id=event_id)
            return updated_event["id"]

        except HttpError as e:
            logger.error("Failed to update event", error=str(e), exc_info=True)
            raise

    def delete_event(self, event_id: str, calendar_id: str = "primary") -> bool:
        """
        Delete an event

        Args:
            event_id: Event ID to delete
            calendar_id: Calendar ID

        Returns:
            True if successful
        """
        try:
            logger.info("Deleting event", event_id=event_id)

            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
            ).execute()

            logger.info("Event deleted successfully", event_id=event_id)
            return True

        except HttpError as e:
            logger.error("Failed to delete event", error=str(e), exc_info=True)
            raise

    def create_reminder(
        self,
        title: str,
        due_date: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a task/reminder (using Calendar events as tasks)

        Args:
            title: Reminder title
            due_date: Due date (ISO 8601)
            description: Reminder description

        Returns:
            Created event/task dictionary
        """
        try:
            logger.info("Creating reminder", title=title, due_date=due_date)

            # Use all-day event as reminder
            event = {
                "summary": f"⏰ REMINDER: {title}",
                "start": {"date": due_date.split("T")[0]},
                "end": {"date": due_date.split("T")[0]},
                "description": description or "",
            }

            created_event = self.service.events().insert(
                calendarId="primary",
                body=event,
            ).execute()

            logger.info("Reminder created successfully", event_id=created_event["id"])
            return created_event

        except Exception as e:
            logger.error("Failed to create reminder", error=str(e), exc_info=True)
            raise


# Global calendar service instance
_calendar_service = None


def get_calendar_service() -> CalendarService:
    """Get or create global calendar service instance"""
    global _calendar_service
    if _calendar_service is None:
        _calendar_service = CalendarService()
    return _calendar_service
