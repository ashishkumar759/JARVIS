from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    """
    Standard response returned by every tool.

    This provides a consistent structure for reporting
    whether a tool succeeded or failed, along with any
    relevant output data.
    """

    success: bool
    message: str
    data: Any = field(default=None)
    error: str | None = None