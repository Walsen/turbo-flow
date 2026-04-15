"""Tests for the backend registry."""

import pytest

from turboflow_adapter.registry import BackendRegistry, registry
from turboflow_adapter.errors import UnknownBackendError
from turboflow_adapter.backend import AgentBackend


class TestRegistry:
    def test_builtin_backends_registered(self) -> None:
        ids = registry.list_ids()
        assert "claude" in ids
        assert "aider" in ids
        assert "openhands" in ids
        assert "strands" in ids

    def test_get_claude(self) -> None:
        backend = registry.get("claude")
        assert backend.name == "Claude Code"
        assert backend.id == "claude"

    def test_get_strands(self) -> None:
        backend = registry.get("strands")
        assert backend.name == "Strands Agents"
        assert backend.id == "strands"

    def test_get_unknown_raises(self) -> None:
        with pytest.raises(UnknownBackendError):
            registry.get("nonexistent")

    def test_has(self) -> None:
        assert registry.has("claude") is True
        assert registry.has("nonexistent") is False

    def test_list_all_returns_info(self) -> None:
        all_backends = registry.list_all()
        assert len(all_backends) >= 4
        names = [b.name for b in all_backends]
        assert "Claude Code" in names
        assert "Strands Agents" in names

    def test_get_returns_same_instance(self) -> None:
        a = registry.get("claude")
        b = registry.get("claude")
        assert a is b

    def test_custom_registration(self) -> None:
        r = BackendRegistry()

        class FakeBackend(AgentBackend):
            name = "Fake"  # type: ignore[assignment]
            description = "Test"  # type: ignore[assignment]
            url = ""  # type: ignore[assignment]
            license = "MIT"  # type: ignore[assignment]
            capabilities = None  # type: ignore[assignment]

            async def exec(self, prompt, options=None):  # type: ignore[override]
                pass

            async def version(self):  # type: ignore[override]
                return "1.0"

            async def is_installed(self):  # type: ignore[override]
                return True

            async def health_check(self):  # type: ignore[override]
                pass

            async def install(self):  # type: ignore[override]
                pass

            def resolve_model(self, model):  # type: ignore[override]
                return model

        r.register("fake", lambda: FakeBackend("fake"))
        assert r.has("fake")
        assert r.get("fake").name == "Fake"
