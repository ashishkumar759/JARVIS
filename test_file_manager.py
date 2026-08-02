import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.file_manager import FileManager


class TestFileManager(unittest.TestCase):
    """
    Validate all low-level FileManager operations.

    Every test uses a temporary directory, so no personal
    or project files are modified.
    """

    def setUp(self):
        self.temp_directory = TemporaryDirectory()
        self.workspace = Path(self.temp_directory.name)

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_create_empty_file(self):
        file_path = self.workspace / "empty.txt"

        result = FileManager.create(str(file_path))

        self.assertTrue(file_path.exists())
        self.assertTrue(file_path.is_file())
        self.assertEqual(file_path.read_text(encoding="utf-8"), "")
        self.assertTrue(result["created"])
        self.assertEqual(result["bytes_written"], 0)

    def test_create_file_with_content(self):
        file_path = self.workspace / "notes.txt"

        result = FileManager.create(
            str(file_path),
            content="Hello JARVIS"
        )

        self.assertTrue(file_path.exists())
        self.assertEqual(
            file_path.read_text(encoding="utf-8"),
            "Hello JARVIS"
        )
        self.assertTrue(result["created"])
        self.assertEqual(
            result["bytes_written"],
            len("Hello JARVIS".encode("utf-8"))
        )

    def test_create_file_with_parent_directories(self):
        file_path = (
            self.workspace
            / "folder_one"
            / "folder_two"
            / "created.txt"
        )

        result = FileManager.create(
            str(file_path),
            content="Nested file",
            create_parents=True
        )

        self.assertTrue(file_path.exists())
        self.assertEqual(
            FileManager.read(str(file_path)),
            "Nested file"
        )
        self.assertTrue(result["created"])

    def test_create_without_existing_parent_fails(self):
        file_path = (
            self.workspace
            / "missing_folder"
            / "file.txt"
        )

        with self.assertRaises(FileNotFoundError):
            FileManager.create(
                str(file_path),
                create_parents=False
            )

    def test_create_existing_file_fails(self):
        file_path = self.workspace / "existing.txt"

        FileManager.create(
            str(file_path),
            content="Original"
        )

        with self.assertRaises(FileExistsError):
            FileManager.create(
                str(file_path),
                content="Replacement"
            )

        self.assertEqual(
            FileManager.read(str(file_path)),
            "Original"
        )

    def test_read_existing_file(self):
        file_path = self.workspace / "read_test.txt"

        FileManager.create(
            str(file_path),
            content="Readable content"
        )

        content = FileManager.read(str(file_path))

        self.assertEqual(content, "Readable content")

    def test_read_missing_file_fails(self):
        file_path = self.workspace / "missing.txt"

        with self.assertRaises(FileNotFoundError):
            FileManager.read(str(file_path))

    def test_read_directory_fails(self):
        with self.assertRaises(IsADirectoryError):
            FileManager.read(str(self.workspace))

    def test_write_overwrites_existing_file(self):
        file_path = self.workspace / "write_test.txt"

        FileManager.create(
            str(file_path),
            content="Old content"
        )

        result = FileManager.write(
            str(file_path),
            content="New content"
        )

        self.assertEqual(
            FileManager.read(str(file_path)),
            "New content"
        )
        self.assertEqual(result["mode"], "overwrite")

    def test_write_appends_to_existing_file(self):
        file_path = self.workspace / "append_test.txt"

        FileManager.create(
            str(file_path),
            content="Hello"
        )

        result = FileManager.write(
            str(file_path),
            content=" JARVIS",
            append=True
        )

        self.assertEqual(
            FileManager.read(str(file_path)),
            "Hello JARVIS"
        )
        self.assertEqual(result["mode"], "append")

    def test_write_empty_content_clears_file(self):
        file_path = self.workspace / "clear_test.txt"

        FileManager.create(
            str(file_path),
            content="This will be cleared."
        )

        result = FileManager.write(
            str(file_path),
            content=""
        )

        self.assertEqual(
            FileManager.read(str(file_path)),
            ""
        )
        self.assertEqual(result["bytes_written"], 0)

    def test_write_missing_file_fails(self):
        file_path = self.workspace / "missing_write.txt"

        with self.assertRaises(FileNotFoundError):
            FileManager.write(
                str(file_path),
                content="Content"
            )

    def test_write_to_directory_fails(self):
        with self.assertRaises(IsADirectoryError):
            FileManager.write(
                str(self.workspace),
                content="Content"
            )

    def test_delete_existing_file(self):
        file_path = self.workspace / "delete_test.txt"

        FileManager.create(
            str(file_path),
            content="Delete me"
        )

        result = FileManager.delete(str(file_path))

        self.assertFalse(file_path.exists())
        self.assertTrue(result["deleted"])

    def test_delete_missing_file_fails(self):
        file_path = self.workspace / "missing_delete.txt"

        with self.assertRaises(FileNotFoundError):
            FileManager.delete(str(file_path))

    def test_delete_directory_fails(self):
        directory = self.workspace / "protected_directory"
        directory.mkdir()

        with self.assertRaises(IsADirectoryError):
            FileManager.delete(str(directory))

        self.assertTrue(directory.exists())

    def test_rename_file(self):
        old_path = self.workspace / "old_name.txt"
        new_path = self.workspace / "new_name.txt"

        FileManager.create(
            str(old_path),
            content="Rename content"
        )

        result = FileManager.rename(
            str(old_path),
            new_name="new_name.txt"
        )

        self.assertFalse(old_path.exists())
        self.assertTrue(new_path.exists())
        self.assertEqual(
            FileManager.read(str(new_path)),
            "Rename content"
        )
        self.assertTrue(result["renamed"])

    def test_rename_with_path_separator_fails(self):
        file_path = self.workspace / "rename_source.txt"

        FileManager.create(
            str(file_path),
            content="Content"
        )

        with self.assertRaises(ValueError):
            FileManager.rename(
                str(file_path),
                new_name="folder/new_name.txt"
            )

        self.assertTrue(file_path.exists())

    def test_rename_to_existing_file_fails_by_default(self):
        source_path = self.workspace / "source.txt"
        destination_path = self.workspace / "destination.txt"

        FileManager.create(
            str(source_path),
            content="Source content"
        )

        FileManager.create(
            str(destination_path),
            content="Destination content"
        )

        with self.assertRaises(FileExistsError):
            FileManager.rename(
                str(source_path),
                new_name="destination.txt"
            )

        self.assertTrue(source_path.exists())
        self.assertEqual(
            FileManager.read(str(destination_path)),
            "Destination content"
        )

    def test_rename_overwrites_when_enabled(self):
        source_path = self.workspace / "rename_source.txt"
        destination_path = self.workspace / "rename_destination.txt"

        FileManager.create(
            str(source_path),
            content="Source wins"
        )

        FileManager.create(
            str(destination_path),
            content="Old destination"
        )

        result = FileManager.rename(
            str(source_path),
            new_name="rename_destination.txt",
            overwrite=True
        )

        self.assertFalse(source_path.exists())
        self.assertTrue(destination_path.exists())
        self.assertEqual(
            FileManager.read(str(destination_path)),
            "Source wins"
        )
        self.assertTrue(result["renamed"])

    def test_copy_file(self):
        source_path = self.workspace / "copy_source.txt"
        destination_path = self.workspace / "copy_destination.txt"

        FileManager.create(
            str(source_path),
            content="Copy content"
        )

        result = FileManager.copy(
            str(source_path),
            str(destination_path)
        )

        self.assertTrue(source_path.exists())
        self.assertTrue(destination_path.exists())
        self.assertEqual(
            FileManager.read(str(destination_path)),
            "Copy content"
        )
        self.assertTrue(result["copied"])

    def test_copy_to_existing_file_fails_by_default(self):
        source_path = self.workspace / "copy_source.txt"
        destination_path = self.workspace / "copy_existing.txt"

        FileManager.create(
            str(source_path),
            content="Source"
        )

        FileManager.create(
            str(destination_path),
            content="Existing"
        )

        with self.assertRaises(FileExistsError):
            FileManager.copy(
                str(source_path),
                str(destination_path)
            )

        self.assertEqual(
            FileManager.read(str(destination_path)),
            "Existing"
        )

    def test_copy_overwrites_when_enabled(self):
        source_path = self.workspace / "copy_source.txt"
        destination_path = self.workspace / "copy_destination.txt"

        FileManager.create(
            str(source_path),
            content="Replacement"
        )

        FileManager.create(
            str(destination_path),
            content="Old content"
        )

        result = FileManager.copy(
            str(source_path),
            str(destination_path),
            overwrite=True
        )

        self.assertEqual(
            FileManager.read(str(destination_path)),
            "Replacement"
        )
        self.assertTrue(result["copied"])

    def test_copy_file_onto_itself_fails(self):
        file_path = self.workspace / "same_copy.txt"

        FileManager.create(
            str(file_path),
            content="Content"
        )

        with self.assertRaises(ValueError):
            FileManager.copy(
                str(file_path),
                str(file_path)
            )

    def test_copy_missing_source_fails(self):
        source_path = self.workspace / "missing_source.txt"
        destination_path = self.workspace / "destination.txt"

        with self.assertRaises(FileNotFoundError):
            FileManager.copy(
                str(source_path),
                str(destination_path)
            )

    def test_move_file(self):
        source_path = self.workspace / "move_source.txt"
        destination_path = self.workspace / "move_destination.txt"

        FileManager.create(
            str(source_path),
            content="Move content"
        )

        result = FileManager.move(
            str(source_path),
            str(destination_path)
        )

        self.assertFalse(source_path.exists())
        self.assertTrue(destination_path.exists())
        self.assertEqual(
            FileManager.read(str(destination_path)),
            "Move content"
        )
        self.assertTrue(result["moved"])

    def test_move_to_existing_file_fails_by_default(self):
        source_path = self.workspace / "move_source.txt"
        destination_path = self.workspace / "move_existing.txt"

        FileManager.create(
            str(source_path),
            content="Source"
        )

        FileManager.create(
            str(destination_path),
            content="Existing"
        )

        with self.assertRaises(FileExistsError):
            FileManager.move(
                str(source_path),
                str(destination_path)
            )

        self.assertTrue(source_path.exists())
        self.assertEqual(
            FileManager.read(str(destination_path)),
            "Existing"
        )

    def test_move_overwrites_when_enabled(self):
        source_path = self.workspace / "move_source.txt"
        destination_path = self.workspace / "move_destination.txt"

        FileManager.create(
            str(source_path),
            content="Replacement"
        )

        FileManager.create(
            str(destination_path),
            content="Old destination"
        )

        result = FileManager.move(
            str(source_path),
            str(destination_path),
            overwrite=True
        )

        self.assertFalse(source_path.exists())
        self.assertTrue(destination_path.exists())
        self.assertEqual(
            FileManager.read(str(destination_path)),
            "Replacement"
        )
        self.assertTrue(result["moved"])

    def test_move_file_onto_itself_fails(self):
        file_path = self.workspace / "same_move.txt"

        FileManager.create(
            str(file_path),
            content="Content"
        )

        with self.assertRaises(ValueError):
            FileManager.move(
                str(file_path),
                str(file_path)
            )

    def test_move_to_missing_parent_fails(self):
        source_path = self.workspace / "source.txt"
        destination_path = (
            self.workspace
            / "missing_directory"
            / "destination.txt"
        )

        FileManager.create(
            str(source_path),
            content="Content"
        )

        with self.assertRaises(FileNotFoundError):
            FileManager.move(
                str(source_path),
                str(destination_path)
            )

        self.assertTrue(source_path.exists())

    def test_empty_path_fails(self):
        with self.assertRaises(ValueError):
            FileManager.read("   ")

    def test_non_string_path_fails(self):
        with self.assertRaises(TypeError):
            FileManager.read(123)


if __name__ == "__main__":
    unittest.main(verbosity=2)