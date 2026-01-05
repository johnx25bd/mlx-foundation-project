"""Domain-specific exceptions for Gmail operations."""


class GmailError(Exception):
    """Base exception for Gmail API errors."""

    pass


class GmailAPIError(GmailError):
    """Error during Gmail API call."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class GmailMessageNotFoundError(GmailAPIError):
    """Message or thread not found."""

    def __init__(self, message_id: str) -> None:
        super().__init__(f"Message not found: {message_id}", status_code=404)
        self.message_id = message_id


class GmailQuotaExceededError(GmailAPIError):
    """Gmail API quota exceeded."""

    def __init__(self) -> None:
        super().__init__("Gmail API quota exceeded. Please try again later.", status_code=429)


class GmailPermissionError(GmailAPIError):
    """Insufficient permissions for Gmail operation."""

    def __init__(self, operation: str) -> None:
        super().__init__(f"Permission denied for operation: {operation}", status_code=403)
        self.operation = operation
