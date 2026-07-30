from tools.base_tool import BaseTool
from tools.tool_metadata import ToolMetadata


class ToolRegistry:
    """
    Maintains a registry of all available JARVIS tools.

    Responsibilities:
    - Register tools
    - Retrieve tools
    - List available tools
    """

    def __init__(self):
        self._tools = {}

    def register(self, tool: BaseTool) -> None:
        """
        Register a tool.

        Raises:
            ValueError if a tool with the same name
            is already registered.
        """

        tool_name = tool.metadata.name

        if tool_name in self._tools:
            raise ValueError(
                f"Tool '{tool_name}' is already registered."
            )

        self._tools[tool_name] = tool




    def get_tool(self, tool_name: str) -> BaseTool | None:
        """
        Retrieve a tool by name.

        Returns:
            BaseTool if found, otherwise None.
        """

        return self._tools.get(tool_name)

    def list_tools(self) -> list[ToolMetadata]:
        """
        Return METADATA all registered tool names.
        """

        return [
            tool.metadata
            for tool in self._tools.values()
        ]

    def get_metadata(
        self,
        tool_name: str
    ) -> ToolMetadata | None:
        """
        Return metadata for a registered tool.
        """

        tool = self.get_tool(tool_name)

        if tool is None:
           return None

        return tool.metadata

    def has_tool(
        self,
        tool_name: str
    ) -> bool:
        """
        Check whether a tool is registered.
        """

        return tool_name in self._tools