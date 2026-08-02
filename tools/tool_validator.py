from tools.constants import ToolErrors
from tools.tool_result import ToolResult


class ToolValidator:
    """
    Utility class providing common validation
    methods for JARVIS tools.
    """

    @staticmethod
    def validate_action(
        tool,
        action: str,
    ) -> ToolResult | None:
        """
        Validate that the tool
        is supported.
        """

        if not tool.supports_action(action):
            return ToolResult(
                success=False,
                message=f"Unsupported action '{action}'.",
                error=ToolErrors.UNSUPPORTED_ACTION
            )

        return None

    @staticmethod
    def require_parameter(
        parameters: dict,
        parameter_name: str
    ) -> ToolResult | None:
        """
        Ensure a required parameter exists.
        """

        if parameter_name not in parameters or parameters[parameter_name] is None:
            return ToolResult(
                success=False,
                message=f"Missing required parameter '{parameter_name}'.",
                error=ToolErrors.MISSING_PARAMETER
            )

        return None