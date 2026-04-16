"""TurboFlow Agent — AgentCore Runtime entry point."""

import os
from strands import Agent
from strands.models.bedrock import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()
log = app.logger

REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")

model = BedrockModel(model_id=MODEL_ID, region_name=REGION)

agent = Agent(
    model=model,
    system_prompt="You are a TurboFlow coding agent. Be concise.",
)


@app.entrypoint
async def invoke(payload, context):
    log.info("Invoking TurboFlow agent")
    prompt = payload.get("prompt", "Hello")
    stream = agent.stream_async(prompt)
    async for event in stream:
        if "data" in event and isinstance(event["data"], str):
            yield event["data"]


if __name__ == "__main__":
    app.run()
