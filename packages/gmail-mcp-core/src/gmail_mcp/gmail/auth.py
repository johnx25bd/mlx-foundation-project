"""OAuth2 authentication for Gmail API."""

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Minimal scopes for required functionality
# gmail.readonly - Read emails
# gmail.compose - Create drafts
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass


def get_credentials(credentials_path: Path, token_path: Path) -> Credentials:
    """Get valid Gmail API credentials, refreshing or re-authenticating as needed.

    Args:
        credentials_path: Path to OAuth client credentials JSON (from Google Cloud Console).
        token_path: Path to store/load user token (auto-generated on first auth).

    Returns:
        Valid Credentials object for Gmail API.

    Raises:
        AuthenticationError: If credentials file not found or auth fails.
    """
    creds: Credentials | None = None

    # Load existing token if available
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except Exception:
            # Token file corrupted or invalid, will re-authenticate
            creds = None

    # Refresh or re-authenticate if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                raise AuthenticationError(f"Failed to refresh token: {e}") from e
        else:
            if not credentials_path.exists():
                raise AuthenticationError(
                    f"OAuth credentials not found at {credentials_path}. "
                    "Download from Google Cloud Console > APIs & Services > Credentials. "
                    "See README for setup instructions."
                )
            try:
                flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                raise AuthenticationError(f"OAuth flow failed: {e}") from e

        # Save token for future use
        if creds:
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text(creds.to_json())

    return creds
