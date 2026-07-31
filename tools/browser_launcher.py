import os
import shutil
import subprocess
import webbrowser
from pathlib import Path


try:
    import winreg
except ImportError:
    winreg = None


class BrowserLauncher:
    """
    Low-level browser launching service.

    Responsibilities:
    - Open URLs in the system's default browser.
    - Open URLs in a specified browser.
    - Pass command-line arguments to a specified browser.
    - Locate installed browser executables on Windows.

    This class does not validate URLs or construct search URLs.
    Those responsibilities belong to BrowserTool.
    """

    @classmethod
    def open(
        cls,
        url: str,
        executable: str | None = None,
        arguments: list[str] | None = None
    ) -> bool:
        """
        Open a URL.

        When executable is None, the operating system's default
        browser is used.

        When executable is provided, the specified browser is
        launched with any provided arguments.

        Args:
            url:
                Valid URL to open.

            executable:
                Browser executable name or full path.

            arguments:
                Optional command-line arguments for the browser.

        Returns:
            True if the launch request succeeded,
            otherwise False.
        """

        browser_arguments = arguments or []

        if executable is None:
            return cls._open_default_browser(
                url=url,
                arguments=browser_arguments
            )

        resolved_executable = cls._resolve_executable(
            executable
        )

        if resolved_executable is None:
            return False

        command = [
            resolved_executable,
            *browser_arguments,
            url,
        ]

        try:
            subprocess.Popen(command)
            return True

        except (FileNotFoundError, OSError):
            return False

    @staticmethod
    def _open_default_browser(
        url: str,
        arguments: list[str]
    ) -> bool:
        """
        Open a URL in the operating system's default browser.

        Command-line arguments cannot reliably be passed to an
        unknown default browser, so arguments are rejected here.
        """

        if arguments:
            return False

        try:
            return bool(
                webbrowser.open(
                    url,
                    new=2
                )
            )

        except webbrowser.Error:
            return False

    @classmethod
    def _resolve_executable(
        cls,
        executable: str
    ) -> str | None:
        """
        Resolve an executable using:

        1. A directly supplied file path.
        2. The operating-system PATH.
        3. The Windows App Paths registry.
        """

        executable_path = Path(executable)

        if executable_path.is_file():
            return str(
                executable_path.resolve()
            )

        path_result = shutil.which(
            executable
        )

        if path_result:
            return path_result

        if os.name == "nt":
            return cls._resolve_windows_app_path(
                executable
            )

        return None

    @staticmethod
    def _resolve_windows_app_path(
        executable: str
    ) -> str | None:
        """
        Locate an installed browser using the Windows
        'App Paths' registry entries.

        This allows applications such as Chrome to be found
        even when their installation directory is not in PATH.
        """

        if winreg is None:
            return None

        registry_path = (
            "SOFTWARE\\Microsoft\\Windows\\CurrentVersion"
            f"\\App Paths\\{executable}"
        )

        registry_hives = (
            winreg.HKEY_CURRENT_USER,
            winreg.HKEY_LOCAL_MACHINE,
        )

        access_modes = (
            winreg.KEY_READ,
            winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
            winreg.KEY_READ | winreg.KEY_WOW64_32KEY,
        )

        for registry_hive in registry_hives:

            for access_mode in access_modes:

                try:
                    with winreg.OpenKey(
                        registry_hive,
                        registry_path,
                        0,
                        access_mode
                    ) as registry_key:

                        executable_path, _ = (
                            winreg.QueryValueEx(
                                registry_key,
                                None
                            )
                        )

                    executable_path = (
                        executable_path
                        .strip()
                        .strip('"')
                    )

                    if Path(executable_path).is_file():
                        return executable_path

                except (
                    FileNotFoundError,
                    OSError
                ):
                    continue

        return None