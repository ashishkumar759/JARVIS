class ApplicationCatalog:
    """
    Maintains a mapping between user-friendly application
    names and their executable commands.
    """

    _APPLICATIONS = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "paint": "mspaint.exe",
        "command prompt": "cmd.exe",
        "cmd": "cmd.exe",
    }

    @classmethod
    def get_executable(cls, app_name: str) -> str | None:
        """
        Return the executable associated with the application.
        """

        return cls._APPLICATIONS.get(app_name.lower())