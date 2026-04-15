"""
Pre-configured TurboFlow agent types.

Each agent type has a tuned system prompt, default model tier, and
appropriate tools. These map to the agent types from AGENTS.md.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from turboflow_adapter.logger import get_logger
from turboflow_adapter.strands.models import ModelTier, create_model
from turboflow_adapter.strands.tools import beads_tools, file_tools, all_tools

log = get_logger("tf-adapter.strands.agents")


class AgentType(str, Enum):
    CODER = "coder"
    TESTER = "tester"
    REVIEWER = "reviewer"
    ARCHITECT = "system-architect"
    RESEARCHER = "researcher"
    COORDINATOR = "coordinator"
    SECURITY = "security-architect"


# ── System prompts per agent type ────────────────────────────────────────

_PROMPTS: dict[AgentType, str] = {
    AgentType.CODER: (
        "You are an expert software developer. Write clean, correct, well-structured code. "
        "Follow the project's existing patterns and conventions. "
        "Always check Beads (bd ready) for context before starting. "
        "After completing work, create a Beads issue to record what was done."
    ),
    AgentType.TESTER: (
        "You are a test engineer. Write thorough tests that cover edge cases, error paths, "
        "and integration points. Use the project's existing test framework. "
        "Run tests after writing them to verify they pass. "
        "Report coverage gaps and suggest additional test scenarios."
    ),
    AgentType.REVIEWER: (
        "You are a senior code reviewer. Analyze code for: "
        "correctness, security vulnerabilities (cite CWE IDs), performance issues, "
        "maintainability, and adherence to project conventions. "
        "Be specific — reference line numbers and suggest concrete fixes. "
        "Check Beads for architectural decisions that inform the review."
    ),
    AgentType.ARCHITECT: (
        "You are a system architect. Design systems with clear boundaries, "
        "well-defined interfaces, and explicit trade-offs. "
        "Consider scalability, reliability, security, and cost. "
        "Document decisions in Beads as type 'decision' with full reasoning. "
        "Use diagrams (mermaid) when they clarify the design."
    ),
    AgentType.RESEARCHER: (
        "You are a technical researcher. Investigate bugs, analyze requirements, "
        "and gather information methodically. "
        "Check Beads and memory for known patterns before investigating. "
        "Document findings with evidence. "
        "If you find a root cause, create a Beads issue with reproduction steps."
    ),
    AgentType.COORDINATOR: (
        "You are a technical lead coordinating a team of specialist agents. "
        "Break complex tasks into subtasks and delegate to the right specialist. "
        "Track progress via Beads. Synthesize results from specialists into a coherent output. "
        "Ensure quality gates pass before considering work complete."
    ),
    AgentType.SECURITY: (
        "You are a security architect. Audit code and designs for vulnerabilities. "
        "Reference OWASP Top 10, CWE IDs, and NIST guidelines. "
        "Check for: injection, auth bypass, data exposure, SSRF, insecure deserialization, "
        "missing input validation, and secrets in code. "
        "Provide severity ratings and concrete remediation steps."
    ),
}

# ── Default model tier per agent type ────────────────────────────────────

_DEFAULT_TIERS: dict[AgentType, ModelTier] = {
    AgentType.CODER: ModelTier.SONNET,
    AgentType.TESTER: ModelTier.SONNET,
    AgentType.REVIEWER: ModelTier.SONNET,
    AgentType.ARCHITECT: ModelTier.OPUS,
    AgentType.RESEARCHER: ModelTier.SONNET,
    AgentType.COORDINATOR: ModelTier.OPUS,
    AgentType.SECURITY: ModelTier.OPUS,
}

# ── Default tools per agent type ─────────────────────────────────────────

_DEFAULT_TOOLS: dict[AgentType, list[str]] = {
    AgentType.CODER: ["all"],
    AgentType.TESTER: ["all"],
    AgentType.REVIEWER: ["beads", "files"],
    AgentType.ARCHITECT: ["beads", "files"],
    AgentType.RESEARCHER: ["all"],
    AgentType.COORDINATOR: ["beads"],
    AgentType.SECURITY: ["beads", "files"],
}


def _resolve_tools(tool_sets: list[str], extra_tools: list | None = None) -> list:
    """Resolve tool set names to actual tool lists."""
    tools: list = []
    for ts in tool_sets:
        if ts == "all":
            tools.extend(all_tools())
        elif ts == "beads":
            tools.extend(beads_tools())
        elif ts == "files":
            tools.extend(file_tools())
    if extra_tools:
        tools.extend(extra_tools)
    return tools


def create_agent(
    agent_type: AgentType | str,
    model_tier: ModelTier | str | None = None,
    system_prompt_override: str | None = None,
    extra_tools: list | None = None,
) -> Any:
    """
    Create a pre-configured TurboFlow Strands agent.

    Args:
        agent_type: The type of agent to create (coder, tester, reviewer, etc.)
        model_tier: Override the default model tier for this agent type
        system_prompt_override: Replace the default system prompt entirely
        extra_tools: Additional Strands tools to add beyond the defaults

    Returns:
        A configured strands.Agent instance ready to invoke.
    """
    from strands import Agent

    if isinstance(agent_type, str):
        agent_type = AgentType(agent_type)

    # Resolve model
    tier = ModelTier(model_tier) if model_tier else _DEFAULT_TIERS[agent_type]
    model = create_model(tier)

    # Resolve system prompt
    prompt = system_prompt_override or _PROMPTS[agent_type]

    # Resolve tools
    tool_set_names = _DEFAULT_TOOLS.get(agent_type, ["all"])
    tools = _resolve_tools(tool_set_names, extra_tools)

    log.info(
        "Creating %s agent (model: %s, tools: %d)",
        agent_type.value,
        tier.value,
        len(tools),
    )

    return Agent(
        model=model,
        system_prompt=prompt,
        tools=tools,
    )
