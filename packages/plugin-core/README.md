# mcp-plugins

Plugin system for MCP servers. Provides abstract base class and registry for extensible plugins.

## Usage

```python
from mcp_plugins import MCPPlugin, PluginRegistry

@PluginRegistry.register
class MyPlugin(MCPPlugin):
    @property
    def name(self) -> str:
        return "my-plugin"

    @property
    def version(self) -> str:
        return "0.1.0"

    def register(self, mcp):
        @mcp.tool()
        def my_tool():
            return "Hello from plugin!"
```
