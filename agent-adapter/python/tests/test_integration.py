"""Integration tests — require Bedrock credentials.

Run with: uv run pytest tests/test_integration.py -v
Skip in CI unless TURBOFLOW_INTEGRATION_TESTS=1 is set.
"""

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("TURBOFLOW_INTEGRATION_TESTS") != "1",
    reason="Integration tests disabled. Set TURBOFLOW_INTEGRATION_TESTS=1 to run.",
)


@pytest.fixture
def bedrock_env() -> None:
    """Ensure Bedrock env is set."""
    assert os.environ.get("CLAUDE_CODE_USE_BEDROCK") == "1", "Set CLAUDE_CODE_USE_BEDROCK=1"
    assert os.environ.get("AWS_REGION"), "Set AWS_REGION"


class TestStrandsIntegration:
    def test_strands_exec_haiku(self, bedrock_env: None) -> None:
        """Test basic Strands execution with Haiku (cheapest model)."""
        import asyncio
        from turboflow_adapter.adapter import AgentAdapter
        from turboflow_adapter.types import ExecOptions

        adapter = AgentAdapter("strands")
        result = asyncio.run(
            adapter.exec(
                "Reply with exactly: INTEGRATION_TEST_OK",
                ExecOptions(model="haiku"),
            )
        )
        assert result.exit_code == 0
        assert "INTEGRATION_TEST_OK" in result.stdout

    def test_create_agent_coder(self, bedrock_env: None) -> None:
        """Test creating a pre-configured coder agent."""
        from turboflow_adapter.strands import create_agent

        agent = create_agent("coder", model_tier="haiku")
        result = agent("Reply with exactly: CODER_AGENT_OK")
        assert "CODER_AGENT_OK" in str(result)

    def test_model_tier_selection(self, bedrock_env: None) -> None:
        """Test that auto tier selection works end-to-end."""
        from turboflow_adapter.strands import create_agent, select_tier

        tier = select_tier("Fix a typo")
        assert tier.value == "haiku"

        agent = create_agent("coder", model_tier=tier)
        result = agent("Reply with exactly: TIER_TEST_OK")
        assert "TIER_TEST_OK" in str(result)
