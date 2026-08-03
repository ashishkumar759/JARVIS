import unittest
from pathlib import Path
from tools.tool_request import ToolRequest
from tools.tool_manager import ToolManager
from tools.constants import ToolActions
from tools.registry import ToolRegistry   # <-- import your registry

class TestFileToolIntegration(unittest.TestCase):
    def setUp(self):
        # Create a temporary test directory
        self.test_dir = Path("temp_test_dir")
        self.test_dir.mkdir(exist_ok=True)

        # Instantiate the registry and pass it to ToolManager
        registry = ToolRegistry()
        self.manager = ToolManager(registry)

    def tearDown(self):
        # Clean up after tests
        for item in self.test_dir.iterdir():
            item.unlink()
        self.test_dir.rmdir()

    def test_copy_file(self):
        source = self.test_dir / "source.txt"
        source.write_text("Hello JARVIS")

        destination = self.test_dir / "copy.txt"

        result = self.manager.execute(
            ToolRequest(
                tool_name="file",
                action=ToolActions.COPY,
                parameters={
                    "source": str(source),
                    "destination": str(destination),
                },
            )
        )

        self.assertTrue(result.success)
        self.assertTrue(source.exists())
        self.assertTrue(destination.exists())
        self.assertEqual(source.read_text(), destination.read_text())
