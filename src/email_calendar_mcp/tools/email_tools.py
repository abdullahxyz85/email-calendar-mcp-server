"""Email tools for MCP"""

from typing import Any

from ..services.email_service import get_email_service
from ..utils.logger import get_logger

logger = get_logger(__name__)


class EmailTools:
    """Email tool implementations"""

    @staticmethod
    def fetch_emails(
        query: str = "",
        max_results: int = 10,
        include_body: bool = False,
    ) -> dict[str, Any]:
        """
        Fetch and search emails from Gmail

        Args:
            query: Gmail search query (e.g., 'from:user@example.com', 'subject:urgent')
            max_results: Maximum emails to return (default: 10)
            include_body: Include full email body (default: False)

        Returns:
            Dictionary with fetched emails or error message
        """
        try:
            service = get_email_service()
            emails = service.fetch_emails(
                query=query,
                max_results=max_results,
                include_body=include_body,
            )
            return {
                "success": True,
                "count": len(emails),
                "emails": emails,
            }
        except Exception as e:
            logger.error("Error fetching emails", error=str(e), exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def send_email(
        to: str,
        subject: str,
        body: str,
        html: bool = False,
        cc: str = "",
        bcc: str = "",
        attachments: list[str] = None,
    ) -> dict[str, Any]:
        """
        Compose and send an email

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
            html: Whether body is HTML formatted (default: False)
            cc: CC recipients (comma-separated)
            bcc: BCC recipients (comma-separated)
            attachments: List of file paths to attach

        Returns:
            Dictionary with sent message ID or error
        """
        try:
            service = get_email_service()
            message_id = service.send_email(
                to=to,
                subject=subject,
                body=body,
                html=html,
                cc=cc if cc else None,
                bcc=bcc if bcc else None,
                attachments=attachments or [],
            )
            return {
                "success": True,
                "message_id": message_id,
                "message": f"Email sent successfully to {to}",
            }
        except Exception as e:
            logger.error("Error sending email", error=str(e), exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def search_emails(query: str, max_results: int = 20) -> dict[str, Any]:
        """
        Search emails using Gmail search syntax

        Args:
            query: Search query (e.g., 'from:john@example.com has:attachment')
            max_results: Maximum results to return

        Returns:
            Dictionary with search results
        """
        try:
            service = get_email_service()
            emails = service.search_emails(query=query, max_results=max_results)
            return {
                "success": True,
                "count": len(emails),
                "emails": emails,
            }
        except Exception as e:
            logger.error("Error searching emails", error=str(e), exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def mark_as_read(message_id: str) -> dict[str, Any]:
        """
        Mark an email as read

        Args:
            message_id: Gmail message ID

        Returns:
            Success status
        """
        try:
            service = get_email_service()
            success = service.mark_as_read(message_id)
            return {
                "success": success,
                "message": "Email marked as read" if success else "Failed to mark email",
            }
        except Exception as e:
            logger.error("Error marking email as read", error=str(e), exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def delete_email(message_id: str) -> dict[str, Any]:
        """
        Delete an email

        Args:
            message_id: Gmail message ID

        Returns:
            Success status
        """
        try:
            service = get_email_service()
            success = service.delete_email(message_id)
            return {
                "success": success,
                "message": "Email deleted" if success else "Failed to delete email",
            }
        except Exception as e:
            logger.error("Error deleting email", error=str(e), exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }


def get_email_tools_definitions() -> list[dict[str, Any]]:
    """
    Get MCP tool definitions for email operations

    Returns:
        List of tool definition dictionaries
    """
    return [
        {
            "name": "fetch_emails",
            "description": "Fetch and search emails from Gmail inbox",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Gmail search query (e.g., 'from:user@example.com', 'subject:important')",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of emails to fetch (default: 10)",
                        "default": 10,
                    },
                    "include_body": {
                        "type": "boolean",
                        "description": "Include full email body (default: False)",
                        "default": False,
                    },
                },
                "required": ["query"],
            },
        },
        {
            "name": "send_email",
            "description": "Compose and send an email via Gmail",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject",
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body text",
                    },
                    "html": {
                        "type": "boolean",
                        "description": "Whether body is HTML formatted (default: False)",
                        "default": False,
                    },
                    "cc": {
                        "type": "string",
                        "description": "CC recipients (comma-separated)",
                    },
                    "bcc": {
                        "type": "string",
                        "description": "BCC recipients (comma-separated)",
                    },
                    "attachments": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of file paths to attach",
                    },
                },
                "required": ["to", "subject", "body"],
            },
        },
        {
            "name": "search_emails",
            "description": "Search emails using Gmail search syntax",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'from:john@example.com has:attachment')",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum results to return (default: 20)",
                        "default": 20,
                    },
                },
                "required": ["query"],
            },
        },
        {
            "name": "mark_as_read",
            "description": "Mark an email as read",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "Gmail message ID",
                    },
                },
                "required": ["message_id"],
            },
        },
        {
            "name": "delete_email",
            "description": "Delete an email",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "Gmail message ID",
                    },
                },
                "required": ["message_id"],
            },
        },
    ]
