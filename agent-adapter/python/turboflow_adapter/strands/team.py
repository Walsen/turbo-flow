"""
Multi-agent team recipes using Strands' agents-as-tools pattern.

Replaces Ruflo's swarm topologies with Strands-native multi-agent patterns.
Each recipe creates a supervisor agent that delegates to specialist agents.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from turboflow_adapter.logger import get_logger
from turboflow_adapter.strands.agents import AgentType, create_agent
from turboflow_adapter.strands.models import ModelTier, create_model
from turboflow_adapter.strands.tools import beads_tools

log = get_logger("tf-adapter.strands.team")

# We need strands for the @tool decorator
try:
    from strands import Agent, tool as strands_tool

    _HAS_STRANDS = True
except ImportError:
    _HAS_STRANDS = False


class TeamRecipe(str, Enum):
    """Pre-built team configurations matching Ruflo swarm recipes."""

    FEATURE = "feature"
    BUG_FIX = "bug-fix"
    CODE_REVIEW = "code-review"
    SECURITY_AUDIT = "security-audit"


def _make_agent_tool(agent_type: AgentType, model_tier: ModelTier | None = None):
    """Wrap a TurboFlow agent as a Strands tool for the supervisor pattern."""
    if not _HAS_STRANDS:
        raise RuntimeError("Strands SDK not installed")

    @strands_tool(
        name=f"{agent_type.value.replace('-', '_')}_agent",
        description=f"Delegate a task to a specialist {agent_type.value} agent.",
    )
    def agent_tool(task: str) -> str:
        agent = create_agent(agent_type, model_tier=model_tier)
        result = agent(task)
        return str(result)

    return agent_tool


def create_team(
    recipe: TeamRecipe | str,
    supervisor_tier: ModelTier | str = ModelTier.OPUS,
) -> Any:
    """
    Create a multi-agent team using the supervisor pattern.

    The supervisor agent delegates to specialist agents exposed as tools.
    This is the Strands equivalent of `rf-swarm`.

    Args:
        recipe: Which team recipe to use
        supervisor_tier: Model tier for the supervisor (default: opus)

    Returns:
        A supervisor strands.Agent that coordinates the specialist team.
    """
    if not _HAS_STRANDS:
        raise RuntimeError("Strands SDK not installed. Run: pip install strands-agents")

    if isinstance(recipe, str):
        recipe = TeamRecipe(recipe)
    if isinstance(supervisor_tier, str):
        supervisor_tier = ModelTier(supervisor_tier)

    builder = _RECIPES[recipe]
    return builder(supervisor_tier)


# ── Recipe builders ──────────────────────────────────────────────────────


def _build_feature_team(supervisor_tier: ModelTier) -> Any:
    """
    Feature team: architect + 2 coders + tester + reviewer.
    Matches the Ruflo "Feature (5 agents)" recipe.
    """
    specialist_tools = [
        _make_agent_tool(AgentType.ARCHITECT, ModelTier.OPUS),
        _make_agent_tool(AgentType.CODER, ModelTier.SONNET),
        _make_agent_tool(AgentType.TESTER, ModelTier.SONNET),
        _make_agent_tool(AgentType.REVIEWER, ModelTier.SONNET),
    ]

    model = create_model(supervisor_tier)

    supervisor = Agent(
        model=model,
        system_prompt=(
            "You are a tech lead coordinating a feature implementation team. "
            "You have specialist agents available as tools: architect, coder, tester, reviewer. "
            "\n\nWorkflow:\n"
            "1. Start by checking project state with beads_ready\n"
            "2. Delegate design to the system_architect_agent\n"
            "3. Delegate implementation to the coder_agent (break into parts if needed)\n"
            "4. Delegate test writing to the tester_agent\n"
            "5. Delegate code review to the reviewer_agent\n"
            "6. Synthesize all results and report the final outcome\n"
            "\nCreate Beads issues to track progress. Record decisions."
        ),
        tools=[*specialist_tools, *beads_tools()],
    )

    log.info("Created feature team (supervisor + 4 specialists)")
    return supervisor


def _build_bugfix_team(supervisor_tier: ModelTier) -> Any:
    """
    Bug fix team: researcher + coder + tester.
    Matches the Ruflo "Bug Fix (3 agents)" recipe.
    """
    specialist_tools = [
        _make_agent_tool(AgentType.RESEARCHER, ModelTier.SONNET),
        _make_agent_tool(AgentType.CODER, ModelTier.SONNET),
        _make_agent_tool(AgentType.TESTER, ModelTier.SONNET),
    ]

    model = create_model(supervisor_tier)

    supervisor = Agent(
        model=model,
        system_prompt=(
            "You are a tech lead coordinating a bug fix. "
            "You have specialist agents: researcher, coder, tester. "
            "\n\nWorkflow:\n"
            "1. Check Beads for known patterns related to this bug\n"
            "2. Delegate investigation to the researcher_agent\n"
            "3. Based on findings, delegate the fix to the coder_agent\n"
            "4. Delegate regression test writing to the tester_agent\n"
            "5. Verify the fix resolves the issue\n"
            "6. Record the fix and root cause in Beads"
        ),
        tools=[*specialist_tools, *beads_tools()],
    )

    log.info("Created bug-fix team (supervisor + 3 specialists)")
    return supervisor


def _build_review_team(supervisor_tier: ModelTier) -> Any:
    """
    Code review team: reviewer + security architect.
    """
    specialist_tools = [
        _make_agent_tool(AgentType.REVIEWER, ModelTier.SONNET),
        _make_agent_tool(AgentType.SECURITY, ModelTier.OPUS),
    ]

    model = create_model(supervisor_tier)

    supervisor = Agent(
        model=model,
        system_prompt=(
            "You are a review coordinator. "
            "You have a code reviewer and a security architect. "
            "\n\nWorkflow:\n"
            "1. Delegate code quality review to the reviewer_agent\n"
            "2. Delegate security audit to the security_architect_agent\n"
            "3. Synthesize both reviews into a unified report\n"
            "4. Prioritize findings by severity\n"
            "5. Record critical findings in Beads"
        ),
        tools=[*specialist_tools, *beads_tools()],
    )

    log.info("Created code-review team (supervisor + 2 specialists)")
    return supervisor


def _build_security_audit_team(supervisor_tier: ModelTier) -> Any:
    """
    Security audit team: security architect + researcher + reviewer.
    """
    specialist_tools = [
        _make_agent_tool(AgentType.SECURITY, ModelTier.OPUS),
        _make_agent_tool(AgentType.RESEARCHER, ModelTier.SONNET),
        _make_agent_tool(AgentType.REVIEWER, ModelTier.SONNET),
    ]

    model = create_model(supervisor_tier)

    supervisor = Agent(
        model=model,
        system_prompt=(
            "You are a security audit coordinator. "
            "You have a security architect, researcher, and code reviewer. "
            "\n\nWorkflow:\n"
            "1. Delegate threat modeling to the security_architect_agent\n"
            "2. Delegate vulnerability research to the researcher_agent\n"
            "3. Delegate code-level review to the reviewer_agent\n"
            "4. Compile a security report with severity ratings\n"
            "5. Record all findings in Beads with type 'bug' and appropriate priority"
        ),
        tools=[*specialist_tools, *beads_tools()],
    )

    log.info("Created security-audit team (supervisor + 3 specialists)")
    return supervisor


_RECIPES = {
    TeamRecipe.FEATURE: _build_feature_team,
    TeamRecipe.BUG_FIX: _build_bugfix_team,
    TeamRecipe.CODE_REVIEW: _build_review_team,
    TeamRecipe.SECURITY_AUDIT: _build_security_audit_team,
}
