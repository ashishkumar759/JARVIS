from tools.registry import ToolRegistry
from tools.tool_loader import load_tools

registry = ToolRegistry()

load_tools(registry)

print(registry.has_tool("app_launcher"))

print(registry.get_metadata("app_launcher"))

print(registry.list_tools())