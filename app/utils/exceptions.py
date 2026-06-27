"""Application exception hierarchy."""


class AppError(Exception):
    """Base class for application errors that map to HTTP responses."""

    status_code = 500
    code = "application_error"

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class ConfigurationError(AppError):
    """Raised when required configuration is missing or invalid."""

    status_code = 500
    code = "configuration_error"


class ToolExecutionError(AppError):
    """Raised when a tool cannot complete its work."""

    status_code = 502
    code = "tool_execution_error"


class LLMError(AppError):
    """Raised when the model or agent fails."""

    status_code = 502
    code = "llm_error"
