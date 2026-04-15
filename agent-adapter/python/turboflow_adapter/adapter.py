"""Main Adapter class — high-level API."""

from __future__ import annotations

import os

from turboflow_adapter.backend import AgentBackend
from turboflow_adapter.errors import BackendNotInstalledError, CapabilityNotSupportedError
from turboflow_adapter.logger import get_logger
from turboflow_adapter.registry import registry, create_backend
from turboflow_adapter.types import (
    BackendInfo,
    ExecOptions,
    ExecResult,
    HealthCheckResult,
    McpServer,
)

log = get_logger("tf-adapter")


class AgentAdapter:
    """High-level adapter that wraps the registry and active backend."""

    def __init__(self, backend_id: str | None = None) -> None:
        id = backend_id or os.environ.get("TURBOFLOW_AGENT_BACKEND", "claude")
        self._backend = create_backend(id)
        log.info("Initialized with backend: %s", self._backend.name)

    @property
    def active_backend(self) -> AgentBackend:
        return self._backend

    @property
    def active_backend_id(self) -> str:
        return self._backend.id

    # ── Backend management ───────────────────────────────────────────────

    async def switch_backend(self, id: str) -> None:
        new_backend = create_backend(id)
        if not await new_backend.is_installed():
            raise BackendNotInstalledError(id)
        self._backend = new_backend
        log.info("Switched to backend: %s", new_backend.name)

    def list_backends(self) -> list[BackendInfo]:
        return registry.list_all()

    async def status(self) -> list[BackendInfo]:
        results = []
        for id in registry.list_ids():
            backend = create_backend(id)
            info = backend.to_info()
            info.installed = await backend.is_installed()
            info.version = await backend.version() if info.installed else None
            info.active = id == self.active_backend_id
            results.append(info)
        return results

    # ── Agent operations ─────────────────────────────────────────────────

    async def exec(self, prompt: str, options: ExecOptions | None = None) -> ExecResult:
        return await self._backend.exec(prompt, options)

    async def version(self) -> str | None:
        return await self._backend.version()

    async def health_check(self) -> HealthCheckResult:
        return await self._backend.health_check()

    async def install(self) -> None:
        return await self._backend.install()

    # ── MCP ──────────────────────────────────────────────────────────────

    async def mcp_add(self, server: McpServer) -> None:
        if not self._backend.has_capability("mcp"):
            log.warning("Backend '%s' does not support MCP", self._backend.name)
            return
        await self._backend.mcp_add(server)

    async def mcp_remove(self, name: str) -> None:
        if not self._backend.has_capability("mcp"):
            return
        await self._backend.mcp_remove(name)

    async def mcp_list(self) -> list[McpServer]:
        if not self._backend.has_capability("mcp"):
            return []
        return await self._backend.mcp_list()

    # ── Capabilities ─────────────────────────────────────────────────────

    def has_capability(self, cap: str) -> bool:
        return self._backend.has_capability(cap)

    def require_capability(self, cap: str) -> None:
        if not self.has_capability(cap):
            raise CapabilityNotSupportedError(self.active_backend_id, cap)

    def resolve_model(self, model: str) -> str:
        return self._backend.resolve_model(model)
