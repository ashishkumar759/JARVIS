import subprocess


class ApplicationLauncher:
    """
    Handles launching desktop applications.

    This class is responsible only for starting
    executables on the operating system.
    """

    @staticmethod
    def launch(executable: str) -> subprocess.Popen:
        """
        Launch an executable.

        Args:
            executable:
                Name or path of the executable.

        Returns:
            subprocess.Popen instance.
        """

        return subprocess.Popen([executable])