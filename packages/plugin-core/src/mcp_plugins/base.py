"""Abstract base class for MCP plugins."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP


class MCPPlugin(ABC):
    """Abstract base class for MCP plugins.

    Plugins extend MCP servers with additional tools, resources, and functionality.
    Implement this class to create a custom plugin.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique plugin identifier."""
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version string (semver recommended)."""
        ...

    @property
    def description(self) -> str:
        """Human-readable plugin description."""
        return ""

    @abstractmethod
    def register(self, mcp: "FastMCP") -> None:
        """Register tools and resources with the MCP server.

        Args:
            mcp: FastMCP server instance to register with.
        """
        ...

    def initialize(self) -> None:  # noqa: B027
        """Optional initialization hook called before registration."""
        pass

    def shutdown(self) -> None:  # noqa: B027
        """Optional cleanup hook called on server shutdown."""
        pass
