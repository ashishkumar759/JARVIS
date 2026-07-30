from tools.application_catalog import ApplicationCatalog
from tools.application_launcher import ApplicationLauncher
from tools.base_tool import BaseTool
from tools.tool_result import ToolResult
from tools.tool_metadata import ToolMetadata
from tools.tool_validator import ToolValidator
from tools.constants import ToolActions, ToolErrors


class AppLauncher(BaseTool):
    """
    Tool responsible for launching desktop applications.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="app_launcher",
            description="Launch desktop applications.",
            supported_actions=(
                ToolActions.OPEN,
            ),
            tags=(
                "desktop",
                "windows",
                "applications",
            ),
        )

    def execute(
        self,
        action: str,
        parameters: dict
    ) -> ToolResult:

        # Validate the requested action.
        validation = ToolValidator.validate_action(
            self,
            action,
        )

        if validation:
            return validation

        # Validate required parameters.
        validation = ToolValidator.require_parameter(
            parameters,
            "target"
        )

        if validation:
            return validation

        target = parameters["target"]

        # Resolve the executable.
        executable = ApplicationCatalog.get_executable(target)

        if executable is None:
            return ToolResult(
                success=False,
                message=f"Unknown application '{target}'.",
                error=ToolErrors.APPLICATION_NOT_FOUND,
            )

        # Attempt to launch the application.
        launched = ApplicationLauncher.launch(executable)

        if launched:
            return ToolResult(
                success=True,
                message=f"Opened '{target}'.",
                data={
                    "target": target,
                    "executable": executable,
                },
            )

        return ToolResult(
            success=False,
            message=f"Failed to open '{target}'.",
            error=ToolErrors.EXECUTION_FAILED,
            data={
                "target": target,
                "executable": executable,
            },
        )