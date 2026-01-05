"""Gmail MCP Server - FastMCP server with Gmail tools."""

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from gmail_mcp.config import get_settings
from gmail_mcp.gmail.auth import get_credentials
from gmail_mcp.gmail.client import GmailClient
from gmail_mcp.gmail.models import DraftReplyResult, UnreadEmailsResult

# Initialize FastMCP server
mcp = FastMCP("Gmail MCP Server")

# Lazy-initialized Gmail client
_gmail_client: GmailClient | None = None


def get_gmail_client() -> GmailClient:
    """Get or create Gmail client with credentials.

    Returns:
        Authenticated GmailClient instance.
    """
    global _gmail_client
    if _gmail_client is None:
        settings = get_settings()
        credentials = get_credentials(settings.credentials_path, settings.token_path)
        _gmail_client = GmailClient(credentials)
    return _gmail_client


@mcp.tool(
    name="get_unread_emails",
    description="Retrieve unread emails from Gmail inbox with sender, subject, body preview, and thread information for replying",
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def get_unread_emails(
    max_results: Annotated[
        int,
        Field(
            default=10,
            ge=1,
            le=50,
            description="Maximum number of emails to return (1-50)",
        ),
    ] = 10,
    labels: Annotated[
        list[str] | None,
        Field(
            default=None,
            description="Gmail labels to filter by (default: INBOX). Example: ['INBOX', 'IMPORTANT']",
        ),
    ] = None,
) -> UnreadEmailsResult:
    """Fetch unread emails from Gmail.

    Returns email summaries including:
    - sender: Email address and display name
    - subject: Email subject line
    - body_preview: First ~500 characters of body
    - email_id: Unique message ID (use with create_draft_reply)
    - thread_id: Thread ID (use with create_draft_reply)

    Use thread_id and email_id with create_draft_reply to respond to emails.
    """
    client = get_gmail_client()
    emails, has_more = await client.get_unread_emails(max_results=max_results, label_ids=labels)

    return UnreadEmailsResult(
        emails=emails,
        total_count=len(emails),
        has_more=has_more,
    )


@mcp.tool(
    name="create_draft_reply",
    description="Create a draft reply to an email thread in Gmail. The draft will be properly threaded with the original conversation.",
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def create_draft_reply(
    thread_id: Annotated[
        str,
        Field(description="Thread ID from get_unread_emails - identifies the conversation"),
    ],
    original_message_id: Annotated[
        str,
        Field(
            description="Message ID (email_id from get_unread_emails) - the specific email being replied to"
        ),
    ],
    reply_body: Annotated[
        str,
        Field(description="Plain text body of the reply message"),
    ],
    original_subject: Annotated[
        str,
        Field(
            description="Subject line of the original email (Re: prefix will be added if needed)"
        ),
    ],
    to_address: Annotated[
        str,
        Field(description="Email address to send the reply to (usually the original sender)"),
    ],
) -> DraftReplyResult:
    """Create a draft reply in an existing email thread.

    The draft is created with proper threading:
    - Attached to the specified thread
    - In-Reply-To and References headers set correctly
    - Subject prefixed with Re: if needed

    The draft can be reviewed and sent from Gmail web or mobile app.
    """
    client = get_gmail_client()
    return await client.create_draft_reply(
        thread_id=thread_id,
        original_message_id=original_message_id,
        reply_body=reply_body,
        original_subject=original_subject,
        to_address=to_address,
    )


def main() -> None:
    """Entry point for CLI."""
    mcp.run()


if __name__ == "__main__":
    main()
