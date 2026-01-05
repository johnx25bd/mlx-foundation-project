#!/usr/bin/env python3
"""Interactive OAuth setup for Gmail MCP server.

This script guides users through the OAuth setup process:
1. Verifies credentials.json exists
2. Runs the OAuth flow to get user authorization
3. Saves the token for future use
"""

import sys
from pathlib import Path

# Add packages to path for direct execution
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "gmail-mcp-core" / "src"))


def print_setup_instructions() -> None:
    """Print OAuth setup instructions."""
    print("=" * 60)
    print("Gmail MCP Server - OAuth Setup")
    print("=" * 60)
    print()
    print("Prerequisites:")
    print("1. Go to https://console.cloud.google.com")
    print("2. Create a new project (or select existing)")
    print("3. Enable the Gmail API:")
    print("   - APIs & Services > Library > Gmail API > Enable")
    print("4. Configure OAuth consent screen:")
    print("   - APIs & Services > OAuth consent screen")
    print("   - Choose 'External' user type")
    print("   - Fill in app name and email")
    print("   - Add scopes: gmail.readonly, gmail.compose")
    print("   - Add your email as a test user")
    print("5. Create OAuth credentials:")
    print("   - APIs & Services > Credentials")
    print("   - Create Credentials > OAuth client ID")
    print("   - Application type: Desktop app")
    print("   - Download JSON and save as credentials.json")
    print()


def main() -> None:
    """Run OAuth setup."""
    print_setup_instructions()

    # Default path
    config_dir = Path.home() / ".config" / "gmail-mcp"
    creds_path = config_dir / "credentials.json"
    token_path = config_dir / "token.json"

    print(f"Expected credentials location: {creds_path}")
    print()

    if not creds_path.exists():
        print(f"[!] Credentials file not found at {creds_path}")
        print()
        print("Please download your OAuth credentials from Google Cloud Console")
        print("and save them to the path above.")
        print()

        # Check if credentials exist elsewhere
        alt_path = Path("credentials.json")
        if alt_path.exists():
            print("Found credentials.json in current directory.")
            response = input("Copy to config directory? [y/N]: ").strip().lower()
            if response == "y":
                config_dir.mkdir(parents=True, exist_ok=True)
                creds_path.write_bytes(alt_path.read_bytes())
                print(f"[OK] Copied to {creds_path}")
            else:
                print("Please manually copy credentials.json to the config directory.")
                sys.exit(1)
        else:
            sys.exit(1)

    print("[OK] Credentials file found!")
    print()
    print("Starting OAuth flow...")
    print("A browser window will open for authorization.")
    print()

    try:
        from gmail_mcp.gmail.auth import get_credentials

        creds = get_credentials(creds_path, token_path)

        print()
        print("[OK] Authentication successful!")
        print(f"Token saved to: {token_path}")
        print(f"Token valid: {creds.valid}")
        print()
        print("You can now use the Gmail MCP server with Claude Desktop.")
        print()
        print("Next steps:")
        print("1. Add the server to your Claude Desktop config")
        print("2. See examples/claude_desktop_config.json for configuration")

    except Exception as e:
        print(f"[ERROR] Authentication failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
