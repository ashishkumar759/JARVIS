from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tools.registry import ToolRegistry
from tools.tool_loader import load_tools
from tools.tool_manager import ToolManager
from tools.tool_request import ToolRequest


class TestFileTool(unittest.TestCase):

    def setUp(self):
        self.temp = TemporaryDirectory()
        self.workspace = Path(self.temp.name)

        registry = ToolRegistry()
        load_tools(registry)

        self.manager = ToolManager(registry)

    def tearDown(self):
        self.temp.cleanup()

    def test_create_read_write_delete(self):

        file_path = self.workspace / "notes.txt"

        result = self.manager.execute(
            ToolRequest(
                tool_name="file",
                action="create",
                parameters={
                    "path": str(file_path),
                    "content": "Hello"
                }
            )
        )

        self.assertTrue(result.success)

        result = self.manager.execute(
            ToolRequest(
                tool_name="file",
                action="read",
                parameters={
                    "path": str(file_path)
                }
            )
        )

        self.assertTrue(result.success)
        self.assertEqual(result.data["content"], "Hello")

        result = self.manager.execute(
            ToolRequest(
                tool_name="file",
                action="write",
                parameters={
                    "path": str(file_path),
                    "content": "JARVIS"
                }
            )
        )

        self.assertTrue(result.success)

        result = self.manager.execute(
            ToolRequest(
                tool_name="file",
                action="read",
                parameters={
                    "path": str(file_path)
                }
            )
        )

        self.assertEqual(
            result.data["content"],
            "JARVIS"
        )

        result = self.manager.execute(
            ToolRequest(
                tool_name="file",
                action="delete",
                parameters={
                    "path": str(file_path)
                }
            )
        )

        self.assertTrue(result.success)

        self.assertFalse(file_path.exists())

    def test_missing_parameter(self):

        result = self.manager.execute(
            ToolRequest(
                tool_name="file",
                action="read"
            )
        )

        self.assertFalse(result.success)

    def test_invalid_action(self):

        result = self.manager.execute(
            ToolRequest(
                tool_name="file",
                action="compress"
            )
        )

        self.assertFalse(result.success)

    def test_unknown_tool(self):

        result = self.manager.execute(
            ToolRequest(
                tool_name="unknown",
                action="read"
            )
        )

        self.assertFalse(result.success)


if __name__ == "__main__":
    unittest.main(verbosity=2)