from tools.registry import ToolRegistry
from tools.implementations.app_launcher import AppLauncher

# Future imports
# from tools.implementations.app_launcher import AppLauncher
# from tools.implementations.browser_tool import BrowserTool


def load_tools(registry: ToolRegistry) -> None:
    """
    Register all available JARVIS tools.

    This function is called once during application startup.
    """

    registry.register(AppLauncher())
    # Future registrations:
    #
    # registry.register(AppLauncher())
    # registry.register(BrowserTool())
    # registry.register(FileTool())
    #
    pass