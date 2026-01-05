"""Configuration management for Gmail MCP server."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Gmail MCP server configuration.

    Configuration can be set via environment variables with GMAIL_MCP_ prefix.
    Example: GMAIL_MCP_CREDENTIALS_PATH=/path/to/credentials.json
    """

    model_config = SettingsConfigDict(
        env_prefix="GMAIL_MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # OAuth paths - credentials.json from Google Cloud Console
    credentials_path: Path = Path.home() / ".config" / "gmail-mcp" / "credentials.json"

    # Token path - auto-generated after first OAuth flow
    token_path: Path = Path.home() / ".config" / "gmail-mcp" / "token.json"

    # Gmail defaults
    default_max_results: int = 10


def get_settings() -> Settings:
    """Get settings instance."""
    return Settings()
