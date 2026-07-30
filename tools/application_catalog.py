class ApplicationCatalog:
    """
    Maintains a mapping between user-friendly application
    names and their executable commands.
    """

    _APPLICATIONS = {

        # -----------------------------
        # Browsers
        # -----------------------------
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "browser": "chrome.exe",

        "edge": "msedge.exe",
        "microsoft edge": "msedge.exe",

        "firefox": "firefox.exe",

        "brave": "brave.exe",
        "brave browser": "brave.exe",

        "opera": "opera.exe",

        # -----------------------------
        # Windows Utilities
        # -----------------------------
        "notepad": "notepad.exe",

        "calculator": "calc.exe",
        "calc": "calc.exe",

        "paint": "mspaint.exe",

        "command prompt": "cmd.exe",
        "cmd": "cmd.exe",

        "powershell": "powershell.exe",
        "power shell": "powershell.exe",

        "file explorer": "explorer.exe",
        "explorer": "explorer.exe",

        "task manager": "taskmgr.exe",

        "registry editor": "regedit.exe",
        "regedit": "regedit.exe",

        "snipping tool": "SnippingTool.exe",

        "character map": "charmap.exe",

        "control panel": "control.exe",

        "settings": "ms-settings:",



    # -----------------------------
        # Development Tools
        # -----------------------------
        "visual studio code": "Code.exe",
        "vs code": "Code.exe",
        "vscode": "Code.exe",
        "code": "Code.exe",

        "pycharm": "pycharm64.exe",
        "pycharm community": "pycharm64.exe",
        "pycharm professional": "pycharm64.exe",

        "intellij": "idea64.exe",
        "intellij idea": "idea64.exe",
        "idea": "idea64.exe",

        "android studio": "studio64.exe",

        "git bash": "git-bash.exe",

        "terminal": "wt.exe",
        "windows terminal": "wt.exe",

        # -----------------------------
        # AI Tools
        # -----------------------------
        "ollama": "ollama.exe",

        "docker": "Docker Desktop.exe",
        "docker desktop": "Docker Desktop.exe",

        "chatgpt": "ChatGPT.exe",
        "chatgpt desktop": "ChatGPT.exe",

        "claude": "Claude.exe",
        "claude desktop": "Claude.exe",

        # -----------------------------
        # Office Applications
        # -----------------------------
        "word": "WINWORD.EXE",
        "microsoft word": "WINWORD.EXE",

        "excel": "EXCEL.EXE",
        "microsoft excel": "EXCEL.EXE",

        "powerpoint": "POWERPNT.EXE",
        "power point": "POWERPNT.EXE",
        "microsoft powerpoint": "POWERPNT.EXE",

        "onenote": "ONENOTE.EXE",

        "outlook": "OUTLOOK.EXE",

        # -----------------------------
        # Communication
        # -----------------------------
        "discord": "Discord.exe",

        "telegram": "Telegram.exe",

        "whatsapp": "WhatsApp.exe",
        "whatsapp desktop": "WhatsApp.exe",

        "slack": "slack.exe",

        "zoom": "Zoom.exe",

        "teams": "Teams.exe",
        "microsoft teams": "Teams.exe",

        # -----------------------------
        # Media
        # -----------------------------
        "vlc": "vlc.exe",
        "vlc media player": "vlc.exe",

        "spotify": "Spotify.exe",

        "windows media player": "wmplayer.exe",
        "fake app": "this_app_does_not_exist.exe"


        
    }

    @classmethod
    def get_executable(cls, app_name: str) -> str | None:
        """
        Return the executable associated with the application.
        """

        normalized_name = cls._normalize_name(app_name)

        return cls._APPLICATIONS.get(normalized_name)

    @staticmethod
    def _normalize_name(app_name: str) -> str:
        """
        Normalize application names before lookup.

        Examples:
            " Chrome "        -> "chrome"
            "GOOGLE CHROME"   -> "google chrome"
            "vs    code"      -> "vs code"
        """

        return " ".join(app_name.strip().lower().split())
