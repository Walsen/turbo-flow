"""
TurboFlow Cloud CLI — invoke deployed agents from anywhere.

Usage:
    tf "Write a fibonacci function"
    tf --model sonnet "Design an auth system"
    tf --status
"""

from __future__ import annotations

import json
import os
import sys

import click

from turboflow_adapter.logger import get_logger

log = get_logger("tf-cloud")

DEFAULT_RUNTIME_ARN = os.environ.get("TURBOFLOW_RUNTIME_ARN", "")
DEFAULT_REGION = os.environ.get("AWS_REGION", "us-east-1")


def _get_client():
    import boto3

    return boto3.client("bedrock-agentcore", region_name=DEFAULT_REGION)


@click.group(invoke_without_command=True)
@click.argument("prompt", required=False)
@click.option("-m", "--model", default=None, help="Model: haiku, sonnet, opus")
@click.option("-r", "--runtime-arn", default=None, help="AgentCore Runtime ARN")
@click.option("--region", default=None, help="AWS region")
@click.pass_context
def main(ctx, prompt, model, runtime_arn, region):
    """TurboFlow Cloud — invoke your deployed agent."""
    if ctx.invoked_subcommand is not None:
        return

    if not prompt:
        click.echo('Usage: tf "your prompt here"')
        click.echo("       tf --status")
        click.echo("       tf --help")
        return

    arn = runtime_arn or DEFAULT_RUNTIME_ARN
    if not arn:
        click.echo(
            "Error: No runtime ARN. Set TURBOFLOW_RUNTIME_ARN or use --runtime-arn",
            err=True,
        )
        sys.exit(1)

    rgn = region or DEFAULT_REGION
    payload: dict = {"prompt": prompt}
    if model:
        model_map = {
            "opus": "us.anthropic.claude-opus-4-6-v1",
            "sonnet": "us.anthropic.claude-sonnet-4-6",
            "haiku": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
        }
        payload["model"] = model_map.get(model, model)

    try:
        import boto3

        client = boto3.client("bedrock-agentcore", region_name=rgn)
        response = client.invoke_agent_runtime(
            agentRuntimeArn=arn,
            payload=json.dumps(payload).encode(),
        )
        output = b""
        for chunk in response.get("response", []):
            if isinstance(chunk, bytes):
                output += chunk
        # Parse streaming response — extract text from SSE data lines
        text = output.decode()
        for line in text.splitlines():
            if line.startswith("data: "):
                data = line[6:].strip()
                if data and data != "[DONE]":
                    # Remove surrounding quotes if present
                    if data.startswith('"') and data.endswith('"'):
                        data = json.loads(data)
                    click.echo(data, nl=False)
        click.echo()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("-r", "--runtime-arn", default=None)
@click.option("--region", default=None)
def status(runtime_arn, region):
    """Show deployed agent status."""
    arn = runtime_arn or DEFAULT_RUNTIME_ARN
    rgn = region or DEFAULT_REGION

    if not arn:
        click.echo("TURBOFLOW_RUNTIME_ARN not set")
        return

    try:
        client = _get_client()
        # Extract runtime ID from ARN
        runtime_id = arn.split("/")[-1]
        response = client.get_agent_runtime(agentRuntimeId=runtime_id)
        click.echo(f"Runtime: {response.get('agentRuntimeName', 'unknown')}")
        click.echo(f"Status: {response.get('status', 'unknown')}")
        click.echo(f"ARN: {arn}")
        click.echo(f"Region: {rgn}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    main()
