from tools.constants import ToolActions
from tools.implementations.app_launcher import AppLauncher

tool = AppLauncher()

result = tool.execute(
    ToolActions.OPEN,
    {}  
)

print(result.success)
print(result.message)
print(result.data)
