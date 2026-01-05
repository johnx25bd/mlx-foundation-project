"""Tests for Pydantic models."""

from datetime import UTC, datetime

from gmail_mcp.gmail.models import DraftReplyResult, EmailSummary, UnreadEmailsResult


class TestEmailSummary:
    """Tests for EmailSummary model."""

    def test_create_with_required_fields(self) -> None:
        """Test creating EmailSummary with required fields."""
        email = EmailSummary(
            email_id="msg123",
            thread_id="thread456",
            sender="test@example.com",
            subject="Test Subject",
            snippet="Short preview",
            body_preview="Full body preview text",
            received_at=datetime.now(UTC),
        )

        assert email.email_id == "msg123"
        assert email.thread_id == "thread456"
        assert email.sender == "test@example.com"
        assert email.subject == "Test Subject"
        assert email.has_attachments is False
        assert email.labels == []

    def test_create_with_all_fields(self) -> None:
        """Test creating EmailSummary with all fields."""
        email = EmailSummary(
            email_id="msg123",
            thread_id="thread456",
            sender="test@example.com",
            sender_name="Test User",
            subject="Test Subject",
            snippet="Short preview",
            body_preview="Full body preview text",
            received_at=datetime.now(UTC),
            has_attachments=True,
            labels=["INBOX", "IMPORTANT"],
        )

        assert email.sender_name == "Test User"
        assert email.has_attachments is True
        assert email.labels == ["INBOX", "IMPORTANT"]


class TestUnreadEmailsResult:
    """Tests for UnreadEmailsResult model."""

    def test_empty_result(self) -> None:
        """Test empty result."""
        result = UnreadEmailsResult(
            emails=[],
            total_count=0,
            has_more=False,
        )

        assert len(result.emails) == 0
        assert result.total_count == 0
        assert result.has_more is False

    def test_result_with_emails(self) -> None:
        """Test result with emails."""
        email = EmailSummary(
            email_id="msg123",
            thread_id="thread456",
            sender="test@example.com",
            subject="Test",
            snippet="Preview",
            body_preview="Body",
            received_at=datetime.now(UTC),
        )

        result = UnreadEmailsResult(
            emails=[email],
            total_count=1,
            has_more=True,
        )

        assert len(result.emails) == 1
        assert result.has_more is True


class TestDraftReplyResult:
    """Tests for DraftReplyResult model."""

    def test_successful_result(self) -> None:
        """Test successful draft creation result."""
        result = DraftReplyResult(
            draft_id="draft123",
            thread_id="thread456",
            message_id="msg789",
            success=True,
        )

        assert result.draft_id == "draft123"
        assert result.success is True

    def test_default_success(self) -> None:
        """Test success defaults to True."""
        result = DraftReplyResult(
            draft_id="draft123",
            thread_id="thread456",
            message_id="msg789",
        )

        assert result.success is True
