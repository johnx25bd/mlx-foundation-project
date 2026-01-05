"""Gmail API client wrapper."""

import asyncio
import base64
import re
from datetime import datetime
from email.mime.text import MIMEText
from email.utils import parsedate_to_datetime
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource, build
from googleapiclient.http import BatchHttpRequest

from gmail_mcp.gmail.models import DraftReplyResult, EmailSummary

# Pre-compiled regex patterns for header parsing
_NAME_PATTERN = re.compile(r'"?([^"<]+)"?\s*<')
_EMAIL_PATTERN = re.compile(r"<([^>]+)>")


class GmailClient:
    """Wrapper for Gmail API operations."""

    def __init__(self, credentials: Credentials) -> None:
        """Initialize Gmail client with credentials.

        Args:
            credentials: Valid OAuth2 credentials for Gmail API.
        """
        self._service: Resource = build("gmail", "v1", credentials=credentials)

    async def get_unread_emails(
        self,
        max_results: int = 10,
        label_ids: list[str] | None = None,
        page_token: str | None = None,
    ) -> tuple[list[EmailSummary], bool, str | None]:
        """Fetch unread emails with summaries.

        Args:
            max_results: Maximum number of emails to return.
            label_ids: Gmail labels to filter by (default: INBOX).
            page_token: Token for pagination (from previous call).

        Returns:
            Tuple of (list of email summaries, has_more flag, next_page_token).
        """
        # Run blocking API calls in thread pool to not block event loop
        return await asyncio.to_thread(
            self._get_unread_emails_sync, max_results, label_ids, page_token
        )

    def _get_unread_emails_sync(
        self,
        max_results: int,
        label_ids: list[str] | None,
        page_token: str | None,
    ) -> tuple[list[EmailSummary], bool, str | None]:
        """Synchronous implementation of get_unread_emails."""
        labels = label_ids or ["INBOX"]

        # List unread messages
        list_params: dict[str, Any] = {
            "userId": "me",
            "q": "is:unread",
            "labelIds": labels,
            "maxResults": max_results,
        }
        if page_token:
            list_params["pageToken"] = page_token

        results = self._service.users().messages().list(**list_params).execute()

        messages = results.get("messages", [])
        has_more = "nextPageToken" in results
        next_page_token = results.get("nextPageToken")

        if not messages:
            return [], has_more, next_page_token

        # Use batch request to fetch all messages in 1-2 API calls (vs N+1)
        # Gmail batch API supports up to 100 requests per batch
        fetched_messages: dict[str, dict[str, Any]] = {}

        def message_callback(request_id: str, response: dict[str, Any], exception: Exception | None) -> None:
            if exception is None:
                fetched_messages[request_id] = response

        batch: BatchHttpRequest = self._service.new_batch_http_request(callback=message_callback)
        for msg in messages:
            batch.add(
                self._service.users().messages().get(
                    userId="me",
                    id=msg["id"],
                    format="full",
                ),
                request_id=msg["id"],
            )
        batch.execute()

        # Parse messages in original order
        emails: list[EmailSummary] = []
        for msg in messages:
            if msg["id"] in fetched_messages:
                emails.append(self._parse_message(fetched_messages[msg["id"]]))

        return emails, has_more, next_page_token

    async def create_draft_reply(
        self,
        thread_id: str,
        original_message_id: str,
        reply_body: str,
        original_subject: str,
        to_address: str,
    ) -> DraftReplyResult:
        """Create a draft reply in a thread.

        Per Gmail API requirements for proper threading:
        - threadId must be specified in the message
        - In-Reply-To header set to original Message-ID
        - References header includes the message thread
        - Subject must match (with Re: prefix if needed)

        Args:
            thread_id: Thread ID to reply in.
            original_message_id: Message ID of the email being replied to.
            reply_body: Plain text body of the reply.
            original_subject: Subject of the original email.
            to_address: Email address to send reply to.

        Returns:
            DraftReplyResult with draft details.
        """
        # Run blocking API calls in thread pool to not block event loop
        return await asyncio.to_thread(
            self._create_draft_reply_sync,
            thread_id,
            original_message_id,
            reply_body,
            original_subject,
            to_address,
        )

    def _create_draft_reply_sync(
        self,
        thread_id: str,
        original_message_id: str,
        reply_body: str,
        original_subject: str,
        to_address: str,
    ) -> DraftReplyResult:
        """Synchronous implementation of create_draft_reply."""
        # Get original message for Message-ID header
        original = (
            self._service.users()
            .messages()
            .get(
                userId="me",
                id=original_message_id,
                format="metadata",
                metadataHeaders=["Message-ID"],
            )
            .execute()
        )

        original_msg_id_header = self._get_header(original, "Message-ID")

        # Build subject with Re: prefix if needed
        subject = original_subject
        if not subject.lower().startswith("re:"):
            subject = f"Re: {subject}"

        # Build MIME message with proper threading headers
        message = MIMEText(reply_body)
        message["to"] = to_address
        message["subject"] = subject

        # Threading headers per RFC 2822
        if original_msg_id_header:
            message["In-Reply-To"] = original_msg_id_header
            message["References"] = original_msg_id_header

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        draft_body = {"message": {"raw": raw, "threadId": thread_id}}

        draft = self._service.users().drafts().create(userId="me", body=draft_body).execute()

        return DraftReplyResult(
            draft_id=draft["id"],
            thread_id=thread_id,
            message_id=draft["message"]["id"],
        )

    def _parse_message(self, msg: dict[str, Any]) -> EmailSummary:
        """Parse Gmail API message into EmailSummary.

        Args:
            msg: Raw message dict from Gmail API.

        Returns:
            Parsed EmailSummary.
        """
        headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}

        sender = headers.get("From", "")
        sender_name = self._extract_name(sender)

        return EmailSummary(
            email_id=msg["id"],
            thread_id=msg["threadId"],
            sender=self._extract_email(sender),
            sender_name=sender_name,
            subject=headers.get("Subject", "(no subject)"),
            snippet=msg.get("snippet", ""),
            body_preview=self._extract_body(msg["payload"])[:500],
            received_at=self._parse_date(headers.get("Date", "")),
            has_attachments=self._has_attachments(msg["payload"]),
            labels=msg.get("labelIds", []),
        )

    def _get_header(self, msg: dict[str, Any], name: str) -> str:
        """Extract header value from message.

        Args:
            msg: Message dict from Gmail API.
            name: Header name to extract.

        Returns:
            Header value or empty string.
        """
        for header in msg.get("payload", {}).get("headers", []):
            if header["name"] == name:
                return header["value"]
        return ""

    def _extract_name(self, from_header: str) -> str | None:
        """Extract display name from From header.

        Args:
            from_header: Full From header value.

        Returns:
            Display name or None.
        """
        # Format: "Display Name <email@example.com>" or just "email@example.com"
        match = _NAME_PATTERN.match(from_header)
        if match:
            return match.group(1).strip()
        return None

    def _extract_email(self, from_header: str) -> str:
        """Extract email address from From header.

        Args:
            from_header: Full From header value.

        Returns:
            Email address.
        """
        match = _EMAIL_PATTERN.search(from_header)
        if match:
            return match.group(1)
        # If no angle brackets, assume the whole thing is an email
        return from_header.strip()

    def _extract_body(self, payload: dict[str, Any]) -> str:
        """Extract plain text body from message payload.

        Args:
            payload: Message payload from Gmail API.

        Returns:
            Decoded body text.
        """
        # Check for direct body data
        if payload.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode(
                "utf-8", errors="replace"
            )

        # Check parts for text/plain
        for part in payload.get("parts", []):
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

            # Recursively check nested parts
            if part.get("parts"):
                result = self._extract_body(part)
                if result:
                    return result

        return ""

    def _parse_date(self, date_str: str) -> datetime:
        """Parse email date header to datetime.

        Args:
            date_str: Date string from email header.

        Returns:
            Parsed datetime (or current time if parsing fails).
        """
        if not date_str:
            return datetime.now()
        try:
            return parsedate_to_datetime(date_str)
        except Exception:
            return datetime.now()

    def _has_attachments(self, payload: dict[str, Any]) -> bool:
        """Check if message has attachments.

        Args:
            payload: Message payload from Gmail API.

        Returns:
            True if message has attachments.
        """
        for part in payload.get("parts", []):
            if part.get("filename"):
                return True
            if part.get("parts") and self._has_attachments(part):
                return True
        return False
