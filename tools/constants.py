class ToolActions:
    """
    Standard tool actions supported by JARVIS.
    """

    OPEN = "open"

    CLOSE = "close"

    START = "start"

    STOP = "stop"

    SEARCH = "search"

    CREATE = "create"

    DELETE = "delete"

    READ = "read"

    WRITE = "write"
    RENAME = "rename"
    COPY = "copy"
    MOVE = "move"




class ToolErrors:
    """
    Standard error codes returned by tools.
    """

    TOOL_NOT_FOUND = "ToolNotFound"

    APPLICATION_NOT_FOUND = "ApplicationNotFound"

    MISSING_TARGET = "MissingTarget"

    UNSUPPORTED_ACTION = "UnsupportedAction"

    NOT_IMPLEMENTED = "NotImplemented"

    EXECUTION_FAILED = "ExecutionFailed"

    MISSING_PARAMETER = "MissingParameter"
    INVALID_PARAMETERS = "InvalidParameters"

    FILE_NOT_FOUND = "FileNotFound"
    FILE_ALREADY_EXISTS = "FileAlreadyExists"
    INVALID_PATH = "InvalidPath"
    NOT_A_FILE = "NotAFile"
    PERMISSION_DENIED = "PermissionDenied"