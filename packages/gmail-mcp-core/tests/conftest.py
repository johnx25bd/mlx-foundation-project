"""Test fixtures for Gmail MCP server."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from gmail_mcp.gmail.client import GmailClient


@pytest.fixture
def sample_message() -> dict[str, Any]:
    """Sample Gmail API message response."""
    return {
        "id": "msg123",
        "threadId": "thread456",
        "snippet": "Hello, this is a test email with some preview text...",
        "labelIds": ["INBOX", "UNREAD"],
        "payload": {
            "headers": [
                {"name": "From", "value": "John Doe <john@example.com>"},
                {"name": "Subject", "value": "Test Email Subject"},
                {"name": "Date", "value": "Mon, 6 Jan 2025 10:00:00 -0500"},
                {"name": "Message-ID", "value": "<abc123@mail.gmail.com>"},
            ],
            "body": {"data": "SGVsbG8gV29ybGQh"},  # base64 "Hello World!"
            "parts": [],
        },
    }


@pytest.fixture
def sample_message_list() -> dict[str, Any]:
    """Sample Gmail API messages.list response."""
    return {
        "messages": [
            {"id": "msg123", "threadId": "thread456"},
            {"id": "msg789", "threadId": "thread012"},
        ],
    }


@pytest.fixture
def mock_gmail_service(
    sample_message: dict[str, Any], sample_message_list: dict[str, Any]
) -> MagicMock:
    """Mock Gmail API service."""
    service = MagicMock()

    # Mock messages().list()
    service.users().messages().list().execute.return_value = sample_message_list

    # Mock messages().get() - return sample message for any ID
    service.users().messages().get().execute.return_value = sample_message

    # Mock drafts().create()
    service.users().drafts().create().execute.return_value = {
        "id": "draft123",
        "message": {"id": "draftmsg456", "threadId": "thread456"},
    }

    return service


@pytest.fixture
def gmail_client(mock_gmail_service: MagicMock) -> GmailClient:
    """Gmail client with mocked service."""
    with patch("gmail_mcp.gmail.client.build") as mock_build:
        mock_build.return_value = mock_gmail_service
        client = GmailClient(MagicMock())  # Mock credentials
        # Replace the service with our mock
        client._service = mock_gmail_service
        return client
