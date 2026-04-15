"""Tests for pre-configured agent types."""

import pytest

from turboflow_adapter.strands.agents import AgentType, _PROMPTS, _DEFAULT_TIERS, _DEFAULT_TOOLS
from turboflow_adapter.strands.models import ModelTier


class TestAgentTypes:
    def test_all_types_have_prompts(self) -> None:
        for agent_type in AgentType:
            assert agent_type in _PROMPTS, f"Missing prompt for {agent_type}"
            assert len(_PROMPTS[agent_type]) > 50, f"Prompt too short for {agent_type}"

    def test_all_types_have_default_tiers(self) -> None:
        for agent_type in AgentType:
            assert agent_type in _DEFAULT_TIERS, f"Missing tier for {agent_type}"

    def test_all_types_have_default_tools(self) -> None:
        for agent_type in AgentType:
            assert agent_type in _DEFAULT_TOOLS, f"Missing tools for {agent_type}"

    def test_architect_uses_opus(self) -> None:
        assert _DEFAULT_TIERS[AgentType.ARCHITECT] == ModelTier.OPUS

    def test_coder_uses_sonnet(self) -> None:
        assert _DEFAULT_TIERS[AgentType.CODER] == ModelTier.SONNET

    def test_security_uses_opus(self) -> None:
        assert _DEFAULT_TIERS[AgentType.SECURITY] == ModelTier.OPUS

    def test_coder_has_all_tools(self) -> None:
        assert "all" in _DEFAULT_TOOLS[AgentType.CODER]

    def test_reviewer_has_no_write(self) -> None:
        tools = _DEFAULT_TOOLS[AgentType.REVIEWER]
        assert "all" not in tools  # reviewer shouldn't have write access by default

    def test_prompts_mention_beads(self) -> None:
        """Agents that have beads tools should mention Beads in their prompt."""
        beads_agents = [
            AgentType.CODER,
            AgentType.ARCHITECT,
            AgentType.RESEARCHER,
            AgentType.COORDINATOR,
        ]
        for agent_type in beads_agents:
            prompt = _PROMPTS[agent_type].lower()
            assert "bead" in prompt, f"{agent_type} prompt should mention Beads"


class TestAgentTypeEnum:
    def test_from_string(self) -> None:
        assert AgentType("coder") == AgentType.CODER
        assert AgentType("system-architect") == AgentType.ARCHITECT

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError):
            AgentType("nonexistent")

    def test_all_values(self) -> None:
        expected = {
            "coder",
            "tester",
            "reviewer",
            "system-architect",
            "researcher",
            "coordinator",
            "security-architect",
        }
        actual = {t.value for t in AgentType}
        assert actual == expected
