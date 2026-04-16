"""
TurboFlow Agent — AgentCore Runtime entry point.

This is the Strands agent that runs inside AgentCore Runtime for each tenant.
It receives prompts via HTTP, creates the appropriate agent type, and returns results.
"""

import os

from strands import Agent
from strands.models.bedrock import BedrockModel
from strands_tools import file_read, file_write, shell
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

# ── Configuration from environment ───────────────────────────────────────
TENANT_ID = os.environ.get("TENANT_ID", "unknown")
TENANT_PLAN = os.environ.get("TENANT_PLAN", "starter")
REGION = os.environ.get("AWS_REGION", "us-east-1")

# Default model based on plan
MODEL_MAP = {
    "starter": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "pro": "us.anthropic.claude-sonnet-4-6",
    "enterprise": "us.anthropic.claude-sonnet-4-6",
}

SYSTEM_PROMPT = f"""You are a TurboFlow coding agent for tenant {TENANT_ID} ({TENANT_PLAN} plan).
You write clean, correct, well-structured code. Follow best practices.
Your workspace is at /mnt/workspace (if available) or the current directory.
Be concise and actionable."""


@app.entrypoint
def handle_request(payload: dict) -> dict:
    """Handle an incoming agent request."""
    prompt = payload.get("prompt", "")
    model_id = payload.get("model", MODEL_MAP.get(TENANT_PLAN, MODEL_MAP["starter"]))
    agent_type = payload.get("agent_type", "coder")

    if not prompt:
        return {"error": "No prompt provided", "tenant_id": TENANT_ID}

    model = BedrockModel(model_id=model_id, region_name=REGION)

    agent = Agent(
        model=model,
        tools=[file_read, file_write, shell],
        system_prompt=SYSTEM_PROMPT,
    )

    result = agent(prompt)

    return {
        "response": str(result),
        "tenant_id": TENANT_ID,
        "model": model_id,
        "agent_type": agent_type,
    }


if __name__ == "__main__":
    app.run()
