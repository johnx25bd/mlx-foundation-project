"""MCP Plugin System - extensible plugin architecture for MCP servers."""

from mcp_plugins.base import MCPPlugin
from mcp_plugins.registry import PluginRegistry

__all__ = ["MCPPlugin", "PluginRegistry"]
