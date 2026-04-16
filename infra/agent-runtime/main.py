"""
TurboFlow Agent — AgentCore Runtime entry point.

This is the same TurboFlow that runs locally, deployed to AgentCore.
All capabilities available locally work here: agent types, team recipes,
auto model routing, Beads memory, GitNexus, AgentDB, observability.

Payload examples:
  {"prompt": "Write a fibonacci function"}
  {"prompt": "...", "agent_type": "reviewer"}
  {"prompt": "...", "agent_type": "security-architect", "model": "opus"}
  {"prompt": "...", "team": "feature"}
  {"prompt": "...", "team": "qa-gate"}
  {"prompt": "...", "team": "full-build"}
"""

import os
import sys

# Ensure turboflow_adapter is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()
log = app.logger

# Set Bedrock as default provider
os.environ.setdefault("CLAUDE_CODE_USE_BEDROCK", "1")
os.environ.setdefault("AWS_REGION", "us-east-1")


@app.entrypoint
async def invoke(payload, context):
    prompt = payload.get("prompt", "")
    if not prompt:
        yield "Error: no prompt provided"
        return

    agent_type = payload.get("agent_type")
    team = payload.get("team")
    model_override = payload.get("model")

    # ── Team recipe ──────────────────────────────────────────────────
    if team:
        log.info("Team recipe: %s", team)
        from turboflow_adapter.strands import create_team

        supervisor = create_team(team)
        stream = supervisor.stream_async(prompt)
        async for event in stream:
            if "data" in event and isinstance(event["data"], str):
                yield event["data"]
        return

    # ── Single agent ─────────────────────────────────────────────────
    if agent_type:
        log.info("Agent type: %s (model: %s)", agent_type, model_override or "default")
        from turboflow_adapter.strands import create_agent

        agent = create_agent(agent_type, model_tier=model_override)
        stream = agent.stream_async(prompt)
        async for event in stream:
            if "data" in event and isinstance(event["data"], str):
                yield event["data"]
        return

    # ── Auto mode — select tier based on prompt complexity ───────────
    log.info("Auto mode — selecting tier based on prompt")
    from turboflow_adapter.strands import create_agent, select_tier

    tier = select_tier(prompt)
    log.info("Auto-selected tier: %s", tier.value)
    agent = create_agent("coder", model_tier=tier)
    stream = agent.stream_async(prompt)
    async for event in stream:
        if "data" in event and isinstance(event["data"], str):
            yield event["data"]


if __name__ == "__main__":
    app.run()
