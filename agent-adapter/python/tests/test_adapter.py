"""Tests for the main adapter class."""

import os
from unittest import mock

import pytest

from turboflow_adapter.adapter import AgentAdapter
from turboflow_adapter.errors import UnknownBackendError


class TestAdapterInit:
    def test_default_backend_claude(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "TURBOFLOW_AGENT_BACKEND"}
        with mock.patch.dict(os.environ, env, clear=True):
            adapter = AgentAdapter()
            assert adapter.active_backend_id == "claude"

    def test_env_backend_override(self) -> None:
        with mock.patch.dict(os.environ, {"TURBOFLOW_AGENT_BACKEND": "strands"}, clear=False):
            adapter = AgentAdapter()
            assert adapter.active_backend_id == "strands"

    def test_explicit_backend(self) -> None:
        adapter = AgentAdapter("aider")
        assert adapter.active_backend_id == "aider"

    def test_unknown_backend_raises(self) -> None:
        with pytest.raises(UnknownBackendError):
            AgentAdapter("nonexistent")


class TestAdapterCapabilities:
    def test_claude_has_mcp(self) -> None:
        adapter = AgentAdapter("claude")
        assert adapter.has_capability("mcp") is True

    def test_aider_no_mcp(self) -> None:
        adapter = AgentAdapter("aider")
        assert adapter.has_capability("mcp") is False

    def test_strands_has_otel(self) -> None:
        adapter = AgentAdapter("strands")
        assert adapter.has_capability("otel") is True

    def test_strands_has_bedrock(self) -> None:
        adapter = AgentAdapter("strands")
        assert adapter.has_capability("bedrock") is True


class TestAdapterModelResolution:
    def test_resolve_sonnet_claude(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_CODE_USE_BEDROCK"}
        with mock.patch.dict(os.environ, env, clear=True):
            adapter = AgentAdapter("claude")
            result = adapter.resolve_model("sonnet")
            assert "sonnet" in result.lower()

    def test_resolve_opus_strands_bedrock(self) -> None:
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_USE_BEDROCK": "1"}, clear=False):
            adapter = AgentAdapter("strands")
            result = adapter.resolve_model("opus")
            assert "opus" in result.lower()

    def test_resolve_passthrough(self) -> None:
        adapter = AgentAdapter("claude")
        result = adapter.resolve_model("custom-model-xyz")
        assert result == "custom-model-xyz"


class TestAdapterListBackends:
    def test_list_backends(self) -> None:
        adapter = AgentAdapter("claude")
        backends = adapter.list_backends()
        ids = [b.id for b in backends]
        assert "claude" in ids
        assert "strands" in ids
        assert len(backends) >= 4
