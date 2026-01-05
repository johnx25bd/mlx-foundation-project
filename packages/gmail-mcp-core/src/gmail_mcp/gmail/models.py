"""Pydantic models for Gmail MCP server."""

from datetime import datetime

from pydantic import BaseModel, Field


class EmailSummary(BaseModel):
    """Summary of an email returned by get_unread_emails."""

    email_id: str = Field(description="Unique Gmail message ID")
    thread_id: str = Field(description="Thread ID for reply threading")
    sender: str = Field(description="Sender email address")
    sender_name: str | None = Field(default=None, description="Sender display name if available")
    subject: str = Field(description="Email subject line")
    snippet: str = Field(description="Short preview of email body (~100 chars)")
    body_preview: str = Field(description="Extended body preview (~500 chars)")
    received_at: datetime = Field(description="When the email was received")
    has_attachments: bool = Field(default=False, description="Whether email has attachments")
    labels: list[str] = Field(default_factory=list, description="Gmail labels on the message")


class UnreadEmailsResult(BaseModel):
    """Result of get_unread_emails tool."""

    emails: list[EmailSummary] = Field(description="List of unread email summaries")
    total_count: int = Field(description="Number of emails returned")
    has_more: bool = Field(description="Whether more unread emails exist beyond the limit")
    next_page_token: str | None = Field(
        default=None, description="Token to fetch next page of results (pass to page_token parameter)"
    )


class DraftReplyResult(BaseModel):
    """Result of create_draft_reply tool."""

    draft_id: str = Field(description="Created draft ID")
    thread_id: str = Field(description="Thread the draft belongs to")
    message_id: str = Field(description="Message ID of the draft")
