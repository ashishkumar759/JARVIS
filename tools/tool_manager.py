from tools.registry import ToolRegistry
from tools.tool_result import ToolResult
from tools.tool_request import ToolRequest  # <-- Import ToolRequest


class ToolManager:
    """
    Coordinates tool execution.

    Responsibilities:
    - Receive execution requests
    - Locate the requested tool
    - Execute the tool
    - Return a ToolResult
    """

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(
        self,
        request: ToolRequest
    ) -> ToolResult:
        """
        Execute a registered tool.

        Args:
            request:
                ToolRequest object containing tool_name, action, and parameters.

        Returns:
            ToolResult
        """

        tool = self.registry.get_tool(request.tool_name)

        if tool is None:
            return ToolResult(
                success=False,
                message=f"Tool '{request.tool_name}' is not registered.",
                error="ToolNotFound"
            )

        try:
            return tool.execute(
                action=request.action,
                parameters=request.parameters or {}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message="Tool execution failed.",
                error=str(e)
            )
