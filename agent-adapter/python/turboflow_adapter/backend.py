"""Abstract backend class — Strategy pattern."""

from __future__ import annotations

from abc import ABC, abstractmethod

from turboflow_adapter.logger import get_logger
from turboflow_adapter.types import (
    BackendCapabilities,
    BackendInfo,
    ExecOptions,
    ExecResult,
    HealthCheckResult,
    McpServer,
)


class AgentBackend(ABC):
    """Base class for all agent backends. Each backend implements this interface."""

    def __init__(self, id: str) -> None:
        self.id = id
        self.log = get_logger(f"tf-adapter.backend.{id}")

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @property
    @abstractmethod
    def url(self) -> str: ...

    @property
    @abstractmethod
    def license(self) -> str: ...

    @property
    @abstractmethod
    def capabilities(self) -> BackendCapabilities: ...

    # ── Core operations ──────────────────────────────────────────────────

    @abstractmethod
    async def exec(self, prompt: str, options: ExecOptions | None = None) -> ExecResult: ...

    @abstractmethod
    async def version(self) -> str | None: ...

    @abstractmethod
    async def is_installed(self) -> bool: ...

    @abstractmethod
    async def health_check(self) -> HealthCheckResult: ...

    @abstractmethod
    async def install(self) -> None: ...

    # ── MCP operations (optional) ────────────────────────────────────────

    async def mcp_add(self, server: McpServer) -> None:
        self.log.warning("MCP not supported by %s", self.name)

    async def mcp_remove(self, name: str) -> None:
        self.log.warning("MCP not supported by %s", self.name)

    async def mcp_list(self) -> list[McpServer]:
        return []

    # ── Model resolution ─────────────────────────────────────────────────

    @abstractmethod
    def resolve_model(self, model: str) -> str: ...

    # ── Helpers ──────────────────────────────────────────────────────────

    def has_capability(self, cap: str) -> bool:
        return getattr(self.capabilities, cap, False)

    def to_info(self) -> BackendInfo:
        return BackendInfo(
            id=self.id,
            name=self.name,
            description=self.description,
            url=self.url,
            license=self.license,
            capabilities=self.capabilities,
        )
