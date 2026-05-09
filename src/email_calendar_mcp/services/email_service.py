"""Email service for Gmail operations"""

import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional, Dict, Any

from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..auth.oauth import get_oauth_manager
from ..utils.logger import get_logger

logger = get_logger(__name__)


class EmailService:
    """Service for Gmail operations"""

    def __init__(self):
        """Initialize email service"""
        self.oauth_manager = get_oauth_manager()
        self.service = None
        self._initialize_service()

    def _initialize_service(self) -> None:
        """Initialize Gmail API service"""
        try:
            credentials = self.oauth_manager.get_credentials()
            self.service = build("gmail", "v1", credentials=credentials)
            logger.info("Gmail service initialized")
        except Exception as e:
            logger.error("Failed to initialize Gmail service", error=str(e), exc_info=True)
            raise

    def fetch_emails(
        self,
        query: str = "",
        max_results: int = 10,
        include_body: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Fetch emails from Gmail

        Args:
            query: Gmail search query (e.g., 'from:sender@example.com', 'subject:important')
            max_results: Maximum number of emails to return
            include_body: Whether to include full email body

        Returns:
            List of email dictionaries with metadata
        """
        try:
            logger.info("Fetching emails", query=query, max_results=max_results)

            # Get message IDs
            results = self.service.users().messages().list(
                userId="me",
                q=query,
                maxResults=min(max_results, 100),  # Gmail API max is 100
            ).execute()

            messages = results.get("messages", [])
            logger.info("Found messages", count=len(messages))

            emails = []
            for message in messages:
                email_data = self._get_message_details(
                    message["id"],
                    include_body=include_body,
                )
                emails.append(email_data)

            return emails
        except HttpError as e:
            logger.error("Failed to fetch emails", error=str(e), exc_info=True)
            raise
        except Exception as e:
            logger.error("Unexpected error fetching emails", error=str(e), exc_info=True)
            raise

    def _get_message_details(self, message_id: str, include_body: bool = False) -> Dict[str, Any]:
        """
        Get details of a specific message

        Args:
            message_id: Gmail message ID
            include_body: Whether to include full body

        Returns:
            Message details dictionary
        """
        try:
            message = self.service.users().messages().get(
                userId="me",
                id=message_id,
                format="full",
            ).execute()

            headers = message["payload"].get("headers", [])
            email_data = {
                "id": message_id,
                "threadId": message.get("threadId"),
                "snippet": message.get("snippet", ""),
                "internalDate": message.get("internalDate"),
            }

            # Extract headers
            for header in headers:
                name = header.get("name", "").lower()
                value = header.get("value", "")

                if name == "from":
                    email_data["from"] = value
                elif name == "to":
                    email_data["to"] = value
                elif name == "subject":
                    email_data["subject"] = value
                elif name == "date":
                    email_data["date"] = value

            # Get body if requested
            if include_body:
                email_data["body"] = self._get_message_body(message)

            return email_data
        except Exception as e:
            logger.error("Failed to get message details", message_id=message_id, error=str(e))
            return {"id": message_id, "error": str(e)}

    def _get_message_body(self, message: Dict[str, Any]) -> str:
        """
        Extract message body from message payload

        Args:
            message: Gmail message object

        Returns:
            Message body text
        """
        try:
            payload = message.get("payload", {})

            # Check for text/plain or text/html parts
            if "parts" in payload:
                # Multipart message
                for part in payload["parts"]:
                    mime_type = part.get("mimeType", "")
                    if mime_type in ["text/plain", "text/html"]:
                        data = part.get("body", {}).get("data", "")
                        if data:
                            return base64.urlsafe_b64decode(data).decode("utf-8")
            else:
                # Simple message
                data = payload.get("body", {}).get("data", "")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8")

            return ""
        except Exception as e:
            logger.error("Failed to extract message body", error=str(e))
            return ""

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        attachments: Optional[List[str]] = None,
    ) -> str:
        """
        Send an email via Gmail

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
            html: Whether body is HTML
            cc: CC recipients (comma-separated)
            bcc: BCC recipients (comma-separated)
            attachments: List of file paths to attach

        Returns:
            Message ID of sent email
        """
        try:
            logger.info("Composing email", to=to, subject=subject)

            message = MIMEMultipart() if attachments else MIMEText(body, "html" if html else "plain")

            message["to"] = to
            message["subject"] = subject

            if cc:
                message["cc"] = cc
            if bcc:
                message["bcc"] = bcc

            # Add body for multipart message
            if attachments:
                message.attach(MIMEText(body, "html" if html else "plain"))

            # Add attachments
            if attachments:
                for attachment_path in attachments:
                    self._attach_file(message, attachment_path)

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send message
            sent_message = self.service.users().messages().send(
                userId="me",
                body={"raw": raw_message},
            ).execute()

            logger.info("Email sent successfully", message_id=sent_message["id"])
            return sent_message["id"]

        except HttpError as e:
            logger.error("Failed to send email", error=str(e), exc_info=True)
            raise
        except Exception as e:
            logger.error("Unexpected error sending email", error=str(e), exc_info=True)
            raise

    def _attach_file(self, message: MIMEMultipart, file_path: str) -> None:
        """
        Attach a file to message

        Args:
            message: MIME message object
            file_path: Path to file to attach
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.warning("Attachment file not found", path=str(file_path))
                return

            # Determine mime type
            mime_type, _ = "application", "octet-stream"
            if file_path.suffix == ".pdf":
                mime_type = "application/pdf"
            elif file_path.suffix in [".txt"]:
                mime_type = "text/plain"

            part = MIMEBase("application", "octet-stream")
            with open(file_path, "rb") as attachment:
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {file_path.name}")
            message.attach(part)

            logger.debug("File attached", filename=file_path.name)
        except Exception as e:
            logger.error("Failed to attach file", file_path=str(file_path), error=str(e))

    def search_emails(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search emails using Gmail search syntax

        Args:
            query: Gmail search query
            max_results: Maximum results to return

        Returns:
            List of matching emails
        """
        return self.fetch_emails(query=query, max_results=max_results)

    def get_email_labels(self) -> List[Dict[str, str]]:
        """
        Get all email labels

        Returns:
            List of label dictionaries
        """
        try:
            results = self.service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])
            logger.info("Labels retrieved", count=len(labels))
            return labels
        except Exception as e:
            logger.error("Failed to get labels", error=str(e), exc_info=True)
            return []

    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark email as read

        Args:
            message_id: Gmail message ID

        Returns:
            True if successful
        """
        try:
            self.service.users().messages().modify(
                userId="me",
                id=message_id,
                body={"removeLabelIds": ["UNREAD"]},
            ).execute()
            logger.info("Email marked as read", message_id=message_id)
            return True
        except Exception as e:
            logger.error("Failed to mark email as read", error=str(e), exc_info=True)
            return False

    def delete_email(self, message_id: str) -> bool:
        """
        Delete an email

        Args:
            message_id: Gmail message ID

        Returns:
            True if successful
        """
        try:
            self.service.users().messages().delete(
                userId="me",
                id=message_id,
            ).execute()
            logger.info("Email deleted", message_id=message_id)
            return True
        except Exception as e:
            logger.error("Failed to delete email", error=str(e), exc_info=True)
            return False


# Global email service instance
_email_service = None


def get_email_service() -> EmailService:
    """Get or create global email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
