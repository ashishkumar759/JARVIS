from tools.registry import ToolRegistry
from tools.tool_loader import load_tools
from tools.tool_manager import ToolManager
from tools.tool_request import ToolRequest


registry = ToolRegistry()
load_tools(registry)

manager = ToolManager(registry)


print("========== TEST 1 ==========")
print(
    manager.execute(
        ToolRequest(
            tool_name="browser",
            action="open",
            parameters={
                "url": "https://openai.com"
            }
        )
    )
)


print("\n========== TEST 2 ==========")
print(
    manager.execute(
        ToolRequest(
            tool_name="browser",
            action="search",
            parameters={
                "query": "Python tutorials"
            }
        )
    )
)


print("\n========== TEST 3 ==========")
print(
    manager.execute(
        ToolRequest(
            tool_name="browser",
            action="open",
            parameters={
                "url": "https://github.com",
                "browser": "chrome"
            }
        )
    )
)


print("\n========== TEST 4 ==========")
print(
    manager.execute(
        ToolRequest(
            tool_name="browser",
            action="open",
            parameters={
                "url": "not_a_url"
            }
        )
    )
)


print("\n========== TEST 5 ==========")
print(
    manager.execute(
        ToolRequest(
            tool_name="browser",
            action="open",
            parameters={
                "url": "https://google.com",
                "browser": "unknown_browser"
            }
        )
    )
)


print("\n========== TEST 6 ==========")
print(
    manager.execute(
        ToolRequest(
            tool_name="browser",
            action="close",
            parameters={}
        )
    )
)