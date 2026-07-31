from urllib.parse import quote_plus
from urllib.parse import urlparse

from tools.base_tool import BaseTool
from tools.browser_catalog import BrowserCatalog
from tools.browser_launcher import BrowserLauncher
from tools.constants import ToolActions, ToolErrors
from tools.tool_metadata import ToolMetadata
from tools.tool_result import ToolResult
from tools.tool_validator import ToolValidator


class BrowserTool(BaseTool):
    """
    Tool responsible for browser operations.

    Supported actions:

    - open
    - search
    """

    SEARCH_ENGINE = "https://www.google.com/search?q={query}"

    @property
    def metadata(self) -> ToolMetadata:

        return ToolMetadata(
            name="browser",
            description="Open web pages and perform web searches.",
            supported_actions=(
                ToolActions.OPEN,
                ToolActions.SEARCH,
            ),
            tags=(
                "browser",
                "internet",
                "web",
            ),
        )

    def execute(
        self,
        action: str,
        parameters: dict,
    ) -> ToolResult:

        validation = ToolValidator.validate_action(
            self,
            action,
        )

        if validation:
            return validation

        if action == ToolActions.OPEN:
            return self._open(parameters)

        if action == ToolActions.SEARCH:
            return self._search(parameters)

        return ToolResult(
            success=False,
            message=f"Unsupported action '{action}'.",
            error=ToolErrors.INVALID_ACTION,
        )

    # --------------------------------------------------
    # OPEN
    # --------------------------------------------------

    def _open(
        self,
        parameters: dict,
    ) -> ToolResult:

        validation = ToolValidator.require_parameter(
            parameters,
            "url",
        )

        if validation:
            return validation

        url = parameters["url"]

        if not self._is_valid_url(url):

            return ToolResult(
                success=False,
                message="Invalid URL.",
                error=ToolErrors.INVALID_PARAMETERS,
            )

        browser = parameters.get("browser")

        executable = None

        if browser:

            executable = BrowserCatalog.get_executable(
                browser
            )

            if executable is None:

                return ToolResult(
                    success=False,
                    message=f"Unknown browser '{browser}'.",
                    error=ToolErrors.APPLICATION_NOT_FOUND,
                )

        arguments = parameters.get(
            "arguments",
            [],
        )

        launched = BrowserLauncher.open(
            url=url,
            executable=executable,
            arguments=arguments,
        )

        if launched:

            return ToolResult(
                success=True,
                message="Browser opened.",
                data={
                    "url": url,
                    "browser": browser,
                },
            )

        return ToolResult(
            success=False,
            message="Failed to launch browser.",
            error=ToolErrors.EXECUTION_FAILED,
        )

    # --------------------------------------------------
    # SEARCH
    # --------------------------------------------------

    def _search(
        self,
        parameters: dict,
    ) -> ToolResult:

        validation = ToolValidator.require_parameter(
            parameters,
            "query",
        )

        if validation:
            return validation

        query = parameters["query"]

        url = self.SEARCH_ENGINE.format(
            query=quote_plus(query)
        )

        browser = parameters.get("browser")

        executable = None

        if browser:

            executable = BrowserCatalog.get_executable(
                browser
            )

            if executable is None:

                return ToolResult(
                    success=False,
                    message=f"Unknown browser '{browser}'.",
                    error=ToolErrors.APPLICATION_NOT_FOUND,
                )

        arguments = parameters.get(
            "arguments",
            [],
        )

        launched = BrowserLauncher.open(
            url=url,
            executable=executable,
            arguments=arguments,
        )

        if launched:

            return ToolResult(
                success=True,
                message=f"Searched '{query}'.",
                data={
                    "query": query,
                    "url": url,
                    "browser": browser,
                },
            )

        return ToolResult(
            success=False,
            message="Failed to launch browser.",
            error=ToolErrors.EXECUTION_FAILED,
        )

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------

    @staticmethod
    def _is_valid_url(
        url: str,
    ) -> bool:

        try:

            parsed = urlparse(url)

            return bool(
                parsed.scheme
                and parsed.netloc
            )

        except Exception:

            return False