"""Tests for model resolution and tier selection."""

import os
from unittest import mock

from turboflow_adapter.strands.models import ModelTier, resolve_model_id, select_tier


class TestResolveModelId:
    def test_sonnet_bedrock(self) -> None:
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_USE_BEDROCK": "1"}, clear=False):
            result = resolve_model_id(ModelTier.SONNET)
            assert "sonnet" in result.lower() or "claude-sonnet" in result

    def test_sonnet_direct(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_CODE_USE_BEDROCK"}
        with mock.patch.dict(os.environ, env, clear=True):
            result = resolve_model_id(ModelTier.SONNET)
            assert "claude-sonnet" in result

    def test_opus_bedrock(self) -> None:
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_USE_BEDROCK": "1"}, clear=False):
            result = resolve_model_id(ModelTier.OPUS)
            assert "opus" in result.lower()

    def test_haiku_bedrock(self) -> None:
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_USE_BEDROCK": "1"}, clear=False):
            result = resolve_model_id(ModelTier.HAIKU)
            assert "haiku" in result.lower()

    def test_env_override(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"CLAUDE_CODE_USE_BEDROCK": "1", "ANTHROPIC_DEFAULT_SONNET_MODEL": "custom-model-id"},
            clear=False,
        ):
            result = resolve_model_id(ModelTier.SONNET)
            assert result == "custom-model-id"


class TestSelectTier:
    def test_simple_task_haiku(self) -> None:
        assert select_tier("Fix typo in README") == ModelTier.HAIKU

    def test_format_task_haiku(self) -> None:
        assert select_tier("Format the JSON config file") == ModelTier.HAIKU

    def test_short_prompt_haiku(self) -> None:
        assert select_tier("Add a comment") == ModelTier.HAIKU

    def test_architecture_task_opus(self) -> None:
        assert (
            select_tier("Design a microservices architecture for the payment system")
            == ModelTier.OPUS
        )

    def test_security_audit_opus(self) -> None:
        assert select_tier("Perform a security audit on the auth module") == ModelTier.OPUS

    def test_long_complex_prompt_opus(self) -> None:
        long_prompt = "Implement a comprehensive " + "feature " * 100 + "with error handling"
        assert select_tier(long_prompt) == ModelTier.OPUS

    def test_standard_coding_sonnet(self) -> None:
        assert (
            select_tier("Implement the user registration endpoint with validation")
            == ModelTier.SONNET
        )

    def test_refactor_opus(self) -> None:
        assert (
            select_tier("Refactor the database layer to use connection pooling") == ModelTier.OPUS
        )
