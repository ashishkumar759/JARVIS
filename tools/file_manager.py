from pathlib import Path
import shutil


class FileManager:
    """
    Low-level filesystem operations.

    This class performs actual file manipulation.
    It does not depend on ToolRequest, ToolResult,
    ToolManager, ToolRegistry, or any other part
    of the Tool Framework.

    FileManager intentionally allows filesystem
    exceptions to propagate to the caller.
    """

    @staticmethod
    def _to_path(path: str) -> Path:
        """
        Convert a path string into a Path object.

        Raises:
            ValueError: If the path is not a non-empty string.
        """
        if not isinstance(path, str):
            raise TypeError("Path must be a string.")

        path = path.strip()

        if not path:
            raise ValueError("Path cannot be empty.")

        return Path(path)

    @staticmethod
    def _require_existing_file(path: Path) -> None:
        """
        Ensure the supplied path exists and points to a file.
        """
        if not path.exists():
            raise FileNotFoundError(f"No such file: '{path}'")

        if path.is_dir():
            raise IsADirectoryError(f"Expected a file but found a directory: '{path}'")

        if not path.is_file():
            raise OSError(f"Path is not a regular file: '{path}'")

    @staticmethod
    def _require_parent_directory(path: Path) -> None:
        """
        Ensure the parent directory of a path exists
        and is actually a directory.
        """
        parent = path.parent

        if not parent.exists():
            raise FileNotFoundError(
                f"Parent directory does not exist: '{parent}'"
            )

        if not parent.is_dir():
            raise NotADirectoryError(
                f"Parent path is not a directory: '{parent}'"
            )

    @staticmethod
    def _same_path(first: Path, second: Path) -> bool:
        """
        Determine whether two paths refer to the same location.

        strict=False allows comparison even when the destination
        does not exist yet.
        """
        return first.resolve(strict=False) == second.resolve(strict=False)

    @staticmethod
    def read(
        path: str,
        encoding: str = "utf-8"
    ) -> str:
        """
        Read and return the contents of an existing text file.
        """
        file_path = FileManager._to_path(path)

        FileManager._require_existing_file(file_path)

        return file_path.read_text(encoding=encoding)

    @staticmethod
    def create(
        path: str,
        content: str = "",
        encoding: str = "utf-8",
        create_parents: bool = False
    ) -> dict:
        """
        Create a new text file.

        Existing files are never overwritten by this method.

        Args:
            path: File path to create.
            content: Initial file content.
            encoding: Text encoding.
            create_parents: Create missing parent directories when True.

        Returns:
            Information about the created file.
        """
        file_path = FileManager._to_path(path)

        if not isinstance(content, str):
            raise TypeError("Content must be a string.")

        if file_path.exists():
            raise FileExistsError(
                f"File already exists: '{file_path}'"
            )

        if create_parents:
            file_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )
        else:
            FileManager._require_parent_directory(file_path)

        file_path.write_text(
            content,
            encoding=encoding
        )

        return {
            "path": str(file_path.resolve()),
            "created": True,
            "bytes_written": len(content.encode(encoding)),
            "encoding": encoding,
        }

    @staticmethod
    def write(
        path: str,
        content: str,
        encoding: str = "utf-8",
        append: bool = False
    ) -> dict:
        """
        Write content to an existing text file.

        By default, the file is overwritten. When append=True,
        the supplied content is added to the end of the file.

        This method does not create a missing file.
        """
        file_path = FileManager._to_path(path)

        if not isinstance(content, str):
            raise TypeError("Content must be a string.")

        if not isinstance(append, bool):
            raise TypeError("Append must be a boolean.")

        FileManager._require_existing_file(file_path)

        mode = "a" if append else "w"

        with file_path.open(
            mode=mode,
            encoding=encoding
        ) as file:
            file.write(content)

        return {
            "path": str(file_path.resolve()),
            "mode": "append" if append else "overwrite",
            "bytes_written": len(content.encode(encoding)),
            "encoding": encoding,
        }

    @staticmethod
    def delete(
        path: str
    ) -> dict:
        """
        Permanently delete an existing file.

        Directories are rejected.
        """
        file_path = FileManager._to_path(path)

        FileManager._require_existing_file(file_path)

        resolved_path = str(file_path.resolve())

        file_path.unlink()

        return {
            "path": resolved_path,
            "deleted": True,
        }

    @staticmethod
    def rename(
        path: str,
        new_name: str,
        overwrite: bool = False
    ) -> dict:
        """
        Rename a file while keeping it in its current directory.

        new_name must contain only a file name, not another
        directory path.
        """
        file_path = FileManager._to_path(path)

        if not isinstance(new_name, str):
            raise TypeError("New name must be a string.")

        new_name = new_name.strip()

        if not new_name:
            raise ValueError("New name cannot be empty.")

        if "/" in new_name or "\\" in new_name:
            raise ValueError(
                "New name must be a file name, not a path."
            )

        if new_name in {".", ".."}:
            raise ValueError("Invalid file name.")

        if not isinstance(overwrite, bool):
            raise TypeError("Overwrite must be a boolean.")

        FileManager._require_existing_file(file_path)

        destination = file_path.with_name(new_name)

        if FileManager._same_path(file_path, destination):
            raise ValueError(
                "The new file name is the same as the current file name."
            )

        if destination.exists():
            if destination.is_dir():
                raise IsADirectoryError(
                    f"Destination is a directory: '{destination}'"
                )

            if not overwrite:
                raise FileExistsError(
                    f"Destination file already exists: '{destination}'"
                )

            file_path.replace(destination)
        else:
            file_path.rename(destination)

        return {
            "old_path": str(file_path.resolve(strict=False)),
            "new_path": str(destination.resolve()),
            "renamed": True,
        }

    @staticmethod
    def copy(
        source: str,
        destination: str,
        overwrite: bool = False
    ) -> dict:
        """
        Copy an existing file to another location.

        The destination is not overwritten unless overwrite=True.
        """
        source_path = FileManager._to_path(source)
        destination_path = FileManager._to_path(destination)

        if not isinstance(overwrite, bool):
            raise TypeError("Overwrite must be a boolean.")

        FileManager._require_existing_file(source_path)
        FileManager._require_parent_directory(destination_path)

        if FileManager._same_path(source_path, destination_path):
            raise ValueError(
                "Source and destination refer to the same file."
            )

        if destination_path.exists():
            if destination_path.is_dir():
                raise IsADirectoryError(
                    f"Destination is a directory: '{destination_path}'"
                )

            if not overwrite:
                raise FileExistsError(
                    f"Destination file already exists: '{destination_path}'"
                )

        shutil.copy2(
            source_path,
            destination_path
        )

        return {
            "source": str(source_path.resolve()),
            "destination": str(destination_path.resolve()),
            "copied": True,
        }

    @staticmethod
    def move(
        source: str,
        destination: str,
        overwrite: bool = False
    ) -> dict:
        """
        Move an existing file to another location.

        The destination is not overwritten unless overwrite=True.
        """
        source_path = FileManager._to_path(source)
        destination_path = FileManager._to_path(destination)

        if not isinstance(overwrite, bool):
            raise TypeError("Overwrite must be a boolean.")

        FileManager._require_existing_file(source_path)
        FileManager._require_parent_directory(destination_path)

        if FileManager._same_path(source_path, destination_path):
            raise ValueError(
                "Source and destination refer to the same file."
            )

        if destination_path.exists():
            if destination_path.is_dir():
                raise IsADirectoryError(
                    f"Destination is a directory: '{destination_path}'"
                )

            if not overwrite:
                raise FileExistsError(
                    f"Destination file already exists: '{destination_path}'"
                )

            destination_path.unlink()

        original_source = str(source_path.resolve())

        moved_path = Path(
            shutil.move(
                str(source_path),
                str(destination_path)
            )
        )

        return {
            "source": original_source,
            "destination": str(moved_path.resolve()),
            "moved": True,
        }