"""Tests for Gmail API client."""

import pytest

from gmail_mcp.gmail.client import GmailClient


class TestGmailClient:
    """Tests for GmailClient."""

    @pytest.mark.asyncio
    async def test_get_unread_emails_returns_list(self, gmail_client: GmailClient) -> None:
        """Test get_unread_emails returns list of emails."""
        emails, has_more, next_page_token = await gmail_client.get_unread_emails(max_results=10)

        assert isinstance(emails, list)
        assert len(emails) == 2  # Mock returns 2 messages
        assert has_more is False
        assert next_page_token is None

    @pytest.mark.asyncio
    async def test_get_unread_emails_parses_sender(self, gmail_client: GmailClient) -> None:
        """Test get_unread_emails correctly parses sender."""
        emails, _, _ = await gmail_client.get_unread_emails()

        assert emails[0].sender == "john@example.com"
        assert emails[0].sender_name == "John Doe"

    @pytest.mark.asyncio
    async def test_get_unread_emails_parses_subject(self, gmail_client: GmailClient) -> None:
        """Test get_unread_emails correctly parses subject."""
        emails, _, _ = await gmail_client.get_unread_emails()

        assert emails[0].subject == "Test Email Subject"

    @pytest.mark.asyncio
    async def test_get_unread_emails_includes_ids(self, gmail_client: GmailClient) -> None:
        """Test get_unread_emails includes email and thread IDs."""
        emails, _, _ = await gmail_client.get_unread_emails()

        assert emails[0].email_id == "msg123"
        assert emails[0].thread_id == "thread456"

    @pytest.mark.asyncio
    async def test_create_draft_reply_returns_result(self, gmail_client: GmailClient) -> None:
        """Test create_draft_reply returns DraftReplyResult."""
        result = await gmail_client.create_draft_reply(
            thread_id="thread456",
            original_message_id="msg123",
            reply_body="Thank you for your email!",
            original_subject="Test Email Subject",
            to_address="john@example.com",
        )

        assert result.draft_id == "draft123"
        assert result.thread_id == "thread456"
        assert result.message_id == "draftmsg456"


class TestGmailClientParsing:
    """Tests for Gmail client parsing methods."""

    def test_extract_name_with_display_name(self, gmail_client: GmailClient) -> None:
        """Test extracting name from From header with display name."""
        name = gmail_client._extract_name("John Doe <john@example.com>")
        assert name == "John Doe"

    def test_extract_name_with_quoted_name(self, gmail_client: GmailClient) -> None:
        """Test extracting name from From header with quoted name."""
        name = gmail_client._extract_name('"John Doe" <john@example.com>')
        assert name == "John Doe"

    def test_extract_name_email_only(self, gmail_client: GmailClient) -> None:
        """Test extracting name when only email present."""
        name = gmail_client._extract_name("john@example.com")
        assert name is None

    def test_extract_email_with_display_name(self, gmail_client: GmailClient) -> None:
        """Test extracting email from From header with display name."""
        email = gmail_client._extract_email("John Doe <john@example.com>")
        assert email == "john@example.com"

    def test_extract_email_only(self, gmail_client: GmailClient) -> None:
        """Test extracting email when only email present."""
        email = gmail_client._extract_email("john@example.com")
        assert email == "john@example.com"
