"""Typed error hierarchy for the Agent Adapter."""


class AdapterError(Exception):
    """Base error for all adapter errors."""

    def __init__(self, message: str, code: str, cause: Exception | None = None):
        super().__init__(message)
        self.code = code
        self.cause = cause


class BackendNotInstalledError(AdapterError):
    """Backend is not installed."""

    def __init__(self, backend: str):
        super().__init__(
            f"Backend '{backend}' is not installed. Run: tf-adapter install {backend}",
            "BACKEND_NOT_INSTALLED",
        )
        self.backend = backend


class UnknownBackendError(AdapterError):
    """Unknown backend identifier."""

    def __init__(self, backend: str, supported: list[str]):
        super().__init__(
            f"Unknown backend '{backend}'. Supported: {', '.join(supported)}",
            "UNKNOWN_BACKEND",
        )
        self.backend = backend
        self.supported = supported


class CapabilityNotSupportedError(AdapterError):
    """Backend doesn't support the requested capability."""

    def __init__(self, backend: str, capability: str):
        super().__init__(
            f"Backend '{backend}' does not support '{capability}'",
            "CAPABILITY_NOT_SUPPORTED",
        )
        self.backend = backend
        self.capability = capability


class ExecError(AdapterError):
    """Agent execution failed."""

    def __init__(self, message: str, exit_code: int, stderr: str, cause: Exception | None = None):
        super().__init__(message, "EXEC_FAILED", cause)
        self.exit_code = exit_code
        self.stderr = stderr


class TimeoutError(AdapterError):
    """Agent execution timed out."""

    def __init__(self, timeout_ms: float):
        super().__init__(
            f"Agent execution timed out after {timeout_ms}ms",
            "EXEC_TIMEOUT",
        )
        self.timeout_ms = timeout_ms


class ConfigError(AdapterError):
    """Configuration error."""

    def __init__(self, message: str, cause: Exception | None = None):
        super().__init__(message, "CONFIG_ERROR", cause)
