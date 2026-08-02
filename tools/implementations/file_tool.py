from pathlib import Path

from tools.base_tool import BaseTool
from tools.constants import ToolActions, ToolErrors
from tools.file_manager import FileManager
from tools.tool_metadata import ToolMetadata
from tools.tool_result import ToolResult
from tools.tool_validator import ToolValidator


class FileTool(BaseTool):
    """
    Tool implementation for local file operations.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="file",
            description="Read, create, write, delete, rename, copy and move local files.",
            supported_actions=[
                ToolActions.READ,
                ToolActions.CREATE,
                ToolActions.WRITE,
                ToolActions.DELETE,
                ToolActions.RENAME,
                ToolActions.COPY,
                ToolActions.MOVE,
            ],
            tags=[
                "filesystem",
                "files",
                "local",
            ],
        )

    def execute(self, action: str, parameters: dict) -> ToolResult:

        validation = ToolValidator.validate_action(
            action,
            self.metadata.supported_actions,
        )

        if validation:
            return validation

        try:

            if action == ToolActions.READ:
                return self._read(parameters)

            if action == ToolActions.CREATE:
                return self._create(parameters)

            if action == ToolActions.WRITE:
                return self._write(parameters)

            if action == ToolActions.DELETE:
                return self._delete(parameters)

            if action == ToolActions.RENAME:
                return self._rename(parameters)

            if action == ToolActions.COPY:
                return self._copy(parameters)

            if action == ToolActions.MOVE:
                return self._move(parameters)

            return ToolResult(
                success=False,
                message=f"Unsupported action '{action}'.",
                error=ToolErrors.UNSUPPORTED_ACTION,
            )

        except Exception as e:
            return self._handle_exception(e)

    def _read(self, parameters):

        validation = ToolValidator.require_parameter(parameters, "path")
        if validation:
            return validation

        path = parameters["path"]
        encoding = parameters.get("encoding", "utf-8")

        content = FileManager.read(path, encoding)

        return ToolResult(
            success=True,
            message="File read successfully.",
            data={
                "path": str(Path(path).resolve()),
                "content": content,
                "encoding": encoding,
            },
        )

    def _create(self, parameters):

        validation = ToolValidator.require_parameter(parameters, "path")
        if validation:
            return validation

        result = FileManager.create(
            path=parameters["path"],
            content=parameters.get("content", ""),
            encoding=parameters.get("encoding", "utf-8"),
            create_parents=parameters.get("create_parents", False),
        )

        return ToolResult(
            success=True,
            message="File created successfully.",
            data=result,
        )

    def _write(self, parameters):

        validation = ToolValidator.require_parameter(parameters, "path")
        if validation:
            return validation

        validation = ToolValidator.require_parameter(parameters, "content")
        if validation:
            return validation

        result = FileManager.write(
            path=parameters["path"],
            content=parameters["content"],
            encoding=parameters.get("encoding", "utf-8"),
            append=parameters.get("append", False),
        )

        return ToolResult(
            success=True,
            message="File written successfully.",
            data=result,
        )

    def _delete(self, parameters):

        validation = ToolValidator.require_parameter(parameters, "path")
        if validation:
            return validation

        result = FileManager.delete(parameters["path"])

        return ToolResult(
            success=True,
            message="File deleted successfully.",
            data=result,
        )

    def _rename(self, parameters):

        validation = ToolValidator.require_parameter(parameters, "path")
        if validation:
            return validation

        validation = ToolValidator.require_parameter(parameters, "new_name")
        if validation:
            return validation

        result = FileManager.rename(
            path=parameters["path"],
            new_name=parameters["new_name"],
            overwrite=parameters.get("overwrite", False),
        )

        return ToolResult(
            success=True,
            message="File renamed successfully.",
            data=result,
        )

    def _copy(self, parameters):

        validation = ToolValidator.require_parameter(parameters, "source")
        if validation:
            return validation

        validation = ToolValidator.require_parameter(parameters, "destination")
        if validation:
            return validation

        result = FileManager.copy(
            source=parameters["source"],
            destination=parameters["destination"],
            overwrite=parameters.get("overwrite", False),
        )

        return ToolResult(
            success=True,
            message="File copied successfully.",
            data=result,
        )

    def _move(self, parameters):

        validation = ToolValidator.require_parameter(parameters, "source")
        if validation:
            return validation

        validation = ToolValidator.require_parameter(parameters, "destination")
        if validation:
            return validation

        result = FileManager.move(
            source=parameters["source"],
            destination=parameters["destination"],
            overwrite=parameters.get("overwrite", False),
        )

        return ToolResult(
            success=True,
            message="File moved successfully.",
            data=result,
        )

    def _handle_exception(self, exception: Exception) -> ToolResult:

        mapping = {
            FileNotFoundError: ToolErrors.FILE_NOT_FOUND,
            FileExistsError: ToolErrors.FILE_ALREADY_EXISTS,
            PermissionError: ToolErrors.PERMISSION_DENIED,
            IsADirectoryError: ToolErrors.NOT_A_FILE,
            NotADirectoryError: ToolErrors.INVALID_PATH,
            ValueError: ToolErrors.INVALID_PARAMETERS,
            TypeError: ToolErrors.INVALID_PARAMETERS,
        }

        for exception_type, error in mapping.items():
            if isinstance(exception, exception_type):
                return ToolResult(
                    success=False,
                    message=str(exception),
                    error=error,
                )

        return ToolResult(
            success=False,
            message=str(exception),
            error=ToolErrors.EXECUTION_FAILED,
        )