"""Gmail API integration."""

from gmail_mcp.gmail.client import GmailClient
from gmail_mcp.gmail.models import DraftReplyResult, EmailSummary, UnreadEmailsResult

__all__ = ["DraftReplyResult", "EmailSummary", "GmailClient", "UnreadEmailsResult"]
