"""TurboFlow Agent Adapter — provider-independent agent abstraction."""

from turboflow_adapter.adapter import AgentAdapter
from turboflow_adapter.backend import AgentBackend
from turboflow_adapter.registry import registry, create_backend
from turboflow_adapter.types import (
    BackendId,
    BackendCapabilities,
    BackendInfo,
    ExecOptions,
    ExecResult,
    HealthCheckResult,
    McpServer,
)
from turboflow_adapter.errors import (
    AdapterError,
    BackendNotInstalledError,
    UnknownBackendError,
    CapabilityNotSupportedError,
    ExecError,
    TimeoutError as AdapterTimeoutError,
    ConfigError,
)

__all__ = [
    "AgentAdapter",
    "AgentBackend",
    "registry",
    "create_backend",
    "BackendId",
    "BackendCapabilities",
    "BackendInfo",
    "ExecOptions",
    "ExecResult",
    "HealthCheckResult",
    "McpServer",
    "AdapterError",
    "BackendNotInstalledError",
    "UnknownBackendError",
    "CapabilityNotSupportedError",
    "ExecError",
    "AdapterTimeoutError",
    "ConfigError",
]
