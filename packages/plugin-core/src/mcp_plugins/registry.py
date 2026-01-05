"""Plugin registry for discovering and managing MCP plugins."""

from typing import TYPE_CHECKING, ClassVar

from mcp_plugins.base import MCPPlugin

if TYPE_CHECKING:
    from fastmcp import FastMCP


class PluginRegistry:
    """Central registry for discovering and managing plugins.

    Use the @PluginRegistry.register decorator to register plugin classes,
    then call load_all() to initialize and register all plugins with a server.
    """

    _plugins: ClassVar[dict[str, type[MCPPlugin]]] = {}
    _instances: ClassVar[dict[str, MCPPlugin]] = {}

    @classmethod
    def register(cls, plugin_class: type[MCPPlugin]) -> type[MCPPlugin]:
        """Decorator to register a plugin class.

        Args:
            plugin_class: Plugin class to register.

        Returns:
            The same plugin class (for use as decorator).
        """
        # Instantiate to get name
        instance = plugin_class()
        cls._plugins[instance.name] = plugin_class
        return plugin_class

    @classmethod
    def get_plugin(cls, name: str) -> MCPPlugin | None:
        """Get or create plugin instance by name.

        Args:
            name: Plugin name to retrieve.

        Returns:
            Plugin instance or None if not found.
        """
        if name not in cls._instances and name in cls._plugins:
            cls._instances[name] = cls._plugins[name]()
        return cls._instances.get(name)

    @classmethod
    def list_plugins(cls) -> list[str]:
        """List all registered plugin names.

        Returns:
            List of registered plugin names.
        """
        return list(cls._plugins.keys())

    @classmethod
    def load_all(cls, mcp: "FastMCP") -> None:
        """Load and register all plugins with the server.

        Args:
            mcp: FastMCP server to register plugins with.
        """
        for name in cls._plugins:
            plugin = cls.get_plugin(name)
            if plugin:
                plugin.initialize()
                plugin.register(mcp)

    @classmethod
    def clear(cls) -> None:
        """Clear all registered plugins (useful for testing)."""
        cls._plugins.clear()
        cls._instances.clear()
