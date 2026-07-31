class BrowserCatalog:
    """
    Maintains browser aliases and their executable names.

    This catalog is intentionally separate from ApplicationCatalog
    because browser operations belong to BrowserTool.
    """

    _BROWSERS = {
        # Google Chrome
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",

        # Microsoft Edge
        "edge": "msedge.exe",
        "microsoft edge": "msedge.exe",

        # Mozilla Firefox
        "firefox": "firefox.exe",
        "mozilla firefox": "firefox.exe",

        # Brave
        "brave": "brave.exe",
        "brave browser": "brave.exe",

        # Opera
        "opera": "opera.exe",
        "opera browser": "opera.exe",
    }

    @classmethod
    def get_executable(
        cls,
        browser_name: str
    ) -> str | None:
        """
        Return the executable associated with a browser alias.

        Args:
            browser_name:
                User-friendly browser name.

        Returns:
            Browser executable name if recognised,
            otherwise None.
        """

        if not isinstance(browser_name, str):
            return None

        normalized_name = cls._normalize_name(
            browser_name
        )

        return cls._BROWSERS.get(
            normalized_name
        )

    @staticmethod
    def _normalize_name(
        browser_name: str
    ) -> str:
        """
        Normalize browser names before lookup.

        Examples:
            " Chrome "          -> "chrome"
            "MICROSOFT EDGE"    -> "microsoft edge"
            "brave    browser"  -> "brave browser"
        """

        return " ".join(
            browser_name.strip().lower().split()
        )