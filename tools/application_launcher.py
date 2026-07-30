import subprocess


class ApplicationLauncher:
    """
    Handles launching desktop applications.

    This class is responsible only for starting
    executables on the operating system.
    """

    @staticmethod
    def launch(executable: str) -> bool:
        """
        Launch an executable.

        Args:
            executable:
                Name or path of the executable.

        Returns:
            True if the application was launched successfully,
            otherwise False.
        """

        try:
            subprocess.Popen([executable])
            return True

        except FileNotFoundError:
            return False

        except OSError:
            return False