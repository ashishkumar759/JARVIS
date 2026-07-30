from abc import ABC, abstractmethod

from tools.tool_result import ToolResult

from tools.tool_metadata import ToolMetadata



class BaseTool(ABC):
    """
    Abstract base class for all JARVIS tools.

    Every tool must inherit from this class and implement
    the required methods.
    """

    @property
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        pass

    @abstractmethod
    def execute(
        self,
        action: str,
        parameters: dict
    ) -> ToolResult:
        """
        Execute the requested action.

        Args:
            action:
                The action to perform
                (e.g. "open", "search", "create").

            parameters:
                Dictionary containing any required inputs.

        Returns:
            ToolResult
        """
        pass

    def supports_action(
        self,
        action: str
    ) -> bool:
        """
        Check whether this tool supports
        the requested action.
        """

        return action in self.metadata.supported_actions