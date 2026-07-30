from dataclasses import dataclass, field


@dataclass(frozen=True)
class ToolMetadata:
    """
    Describes a JARVIS tool.

    Metadata is used for discovery,
    planning, documentation, and UI.
    """

    name: str

    description: str

    supported_actions: tuple[str, ...]

    version: str = "1.0"

    tags: tuple[str, ...] = field(default_factory=tuple)