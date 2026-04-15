"""Backend Registry — Factory + Registry pattern."""

from __future__ import annotations

from typing import Callable

from turboflow_adapter.backend import AgentBackend
from turboflow_adapter.errors import UnknownBackendError
from turboflow_adapter.logger import get_logger
from turboflow_adapter.types import BackendInfo

log = get_logger("tf-adapter.registry")

BackendFactory = Callable[[], AgentBackend]


class BackendRegistry:
    """Central registry for all backends. Supports dynamic registration."""

    def __init__(self) -> None:
        self._factories: dict[str, BackendFactory] = {}
        self._instances: dict[str, AgentBackend] = {}
        self._register_builtins()

    def _register_builtins(self) -> None:
        from turboflow_adapter.backends.claude import ClaudeBackend
        from turboflow_adapter.backends.aider import AiderBackend
        from turboflow_adapter.backends.openhands import OpenHandsBackend
        from turboflow_adapter.backends.strands import StrandsBackend

        self.register("claude", ClaudeBackend)
        self.register("aider", AiderBackend)
        self.register("openhands", OpenHandsBackend)
        self.register("strands", StrandsBackend)

    def register(self, id: str, factory: BackendFactory) -> None:
        self._factories[id] = factory
        log.debug("Backend registered: %s", id)

    def get(self, id: str) -> AgentBackend:
        if id in self._instances:
            return self._instances[id]

        factory = self._factories.get(id)
        if not factory:
            raise UnknownBackendError(id, self.list_ids())

        instance = factory()
        self._instances[id] = instance
        return instance

    def has(self, id: str) -> bool:
        return id in self._factories

    def list_ids(self) -> list[str]:
        return list(self._factories.keys())

    def list_all(self) -> list[BackendInfo]:
        return [self.get(id).to_info() for id in self.list_ids()]


# Singleton
registry = BackendRegistry()


def create_backend(id: str) -> AgentBackend:
    """Factory function — get a backend by ID."""
    return registry.get(id)
