from dataclasses import dataclass, field


@dataclass
class ToolRequest:
    """
    Standard request object passed to tools.

    This provides a consistent structure for
    tool execution requests.
    """

    tool_name: str

    action: str

    parameters: dict = field(default_factory=dict)