"""
TurboFlow unified CLI.

Usage:
    tf "Write a fibonacci function"              # auto: cloud if deployed, local otherwise
    tf --cloud "prompt"                          # force cloud (AgentCore)
    tf --local "prompt"                          # force local (Strands)
    tf --local --backend aider "prompt"          # specific local backend
    tf --model sonnet "prompt"                   # model override
    tf status                                    # show local + cloud status
    tf health                                    # health check
    tf backends                                  # list local backends
    tf mcp list                                  # MCP servers
"""

from __future__ import annotations

import asyncio
import json
import os
import sys

import click

from turboflow_adapter.adapter import AgentAdapter
from turboflow_adapter.types import ExecOptions

_RUNTIME_ARN = os.environ.get("TURBOFLOW_RUNTIME_ARN", "")
_REGION = os.environ.get("AWS_REGION", "us-east-1")

_MODEL_MAP = {
    "opus": "us.anthropic.claude-opus-4-6-v1",
    "sonnet": "us.anthropic.claude-sonnet-4-6",
    "haiku": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
}


def _run(coro):  # type: ignore
    """Run an async function synchronously."""
    return asyncio.run(coro)


def _has_cloud() -> bool:
    return bool(_RUNTIME_ARN)


def _invoke_cloud(
    prompt: str,
    model: str | None = None,
    runtime_arn: str | None = None,
    agent_type: str | None = None,
    team: str | None = None,
) -> None:
    """Invoke the deployed agent on AgentCore."""
    import boto3

    arn = runtime_arn or _RUNTIME_ARN
    payload: dict = {"prompt": prompt}
    if model:
        payload["model"] = _MODEL_MAP.get(model, model)
    if agent_type:
        payload["agent_type"] = agent_type
    if team:
        payload["team"] = team

    client = boto3.client("bedrock-agentcore", region_name=_REGION)
    response = client.invoke_agent_runtime(
        agentRuntimeArn=arn,
        payload=json.dumps(payload).encode(),
    )
    output = b""
    for chunk in response.get("response", []):
        if isinstance(chunk, bytes):
            output += chunk
    text = output.decode()
    for line in text.splitlines():
        if line.startswith("data: "):
            data = line[6:].strip()
            if data and data != "[DONE]":
                if data.startswith('"') and data.endswith('"'):
                    data = json.loads(data)
                click.echo(data, nl=False)
    click.echo()


def _invoke_local(
    prompt: str,
    backend: str | None = None,
    model: str | None = None,
    files: tuple = (),
    system_prompt: str | None = None,
    timeout: float | None = None,
) -> None:
    """Invoke a local agent backend."""
    adapter = AgentAdapter(backend)
    result = _run(
        adapter.exec(
            prompt,
            ExecOptions(
                files=list(files) if files else None,
                model=model,
                headless=True,
                system_prompt=system_prompt,
                timeout=timeout,
            ),
        )
    )
    if result.stdout:
        click.echo(result.stdout)
    if result.stderr:
        click.echo(result.stderr, err=True)
    sys.exit(result.exit_code)


# ── Main command ─────────────────────────────────────────────────────────


@click.group(invoke_without_command=True)
@click.argument("prompt", required=False)
@click.option("-m", "--model", help="Model: haiku, sonnet, opus (or backend-specific)")
@click.option("-b", "--backend", help="Local backend: strands, claude, aider, openhands, kiro")
@click.option(
    "-a",
    "--agent",
    "agent_type",
    help="Agent type: coder, tester, reviewer, system-architect, researcher, security-architect",
)
@click.option(
    "--team",
    help="Team recipe: feature, bug-fix, code-review, security-audit, qa-gate, tdd, full-build",
)
@click.option("-f", "--file", "files", multiple=True, help="Target file(s)")
@click.option("-s", "--system-prompt", help="System prompt override")
@click.option("-t", "--timeout", type=float, help="Timeout in seconds")
@click.option("--cloud", "force_cloud", is_flag=True, help="Force cloud execution (AgentCore)")
@click.option("--local", "force_local", is_flag=True, help="Force local execution")
@click.option("-r", "--runtime-arn", help="AgentCore Runtime ARN override")
@click.version_option(version="0.1.0")
@click.pass_context
def main(
    ctx,
    prompt,
    model,
    backend,
    agent_type,
    team,
    files,
    system_prompt,
    timeout,
    force_cloud,
    force_local,
    runtime_arn,
):
    """TurboFlow — invoke AI agents locally or in the cloud."""
    if ctx.invoked_subcommand is not None:
        return

    if not prompt:
        click.echo('Usage: tf "your prompt"')
        click.echo("")
        click.echo("Options:")
        click.echo('  tf "prompt"                          auto (cloud or local)')
        click.echo('  tf -a reviewer "prompt"              specific agent type')
        click.echo('  tf --team feature "prompt"           multi-agent team')
        click.echo('  tf --cloud "prompt"                  force cloud (AgentCore)')
        click.echo('  tf --local "prompt"                  force local (Strands)')
        click.echo('  tf --local -b aider "prompt"         specific local backend')
        click.echo('  tf -m sonnet "prompt"                model override')
        click.echo("  tf status                            show status")
        click.echo("  tf backends                          list backends")
        return

    try:
        if force_cloud:
            arn = runtime_arn or _RUNTIME_ARN
            if not arn:
                click.echo(
                    "Error: No runtime ARN. Set TURBOFLOW_RUNTIME_ARN or use --runtime-arn",
                    err=True,
                )
                sys.exit(1)
            _invoke_cloud(prompt, model, arn, agent_type=agent_type, team=team)
        elif force_local or backend:
            _invoke_local(prompt, backend, model, files, system_prompt, timeout)
        elif _has_cloud():
            # Auto: cloud if deployed
            _invoke_cloud(prompt, model, runtime_arn, agent_type=agent_type, team=team)
        else:
            # Auto: local fallback
            _invoke_local(prompt, backend, model, files, system_prompt, timeout)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ── Status ───────────────────────────────────────────────────────────────


@main.command()
def status():
    """Show local backends + cloud deployment status."""
    # Local backends
    adapter = AgentAdapter()
    statuses = _run(adapter.status())

    click.echo("╔══════════════════════════════════════════╗")
    click.echo("║         TurboFlow Status                  ║")
    click.echo("╚══════════════════════════════════════════╝")
    click.echo()
    click.echo("Local backends:")
    for s in statuses:
        active = " (active)" if s.active else ""
        icon = "✓" if s.installed else "✗"
        ver = f" — {s.version}" if s.version else ""
        click.echo(f"  {icon} {s.name}{active}{ver}")

    # Cloud
    click.echo()
    click.echo("Cloud (AgentCore):")
    if _has_cloud():
        click.echo(f"  ✓ Deployed: {_RUNTIME_ARN}")
        click.echo(f"    Region: {_REGION}")
    else:
        click.echo("  ✗ Not configured (set TURBOFLOW_RUNTIME_ARN)")


@main.command()
@click.option("-b", "--backend", help="Check a specific backend")
def health(backend):
    """Run health check on a backend."""
    adapter = AgentAdapter(backend)
    h = _run(adapter.health_check())

    click.echo(f"Backend: {adapter.active_backend_id}")
    click.echo(f"Installed: {'✓' if h.installed else '✗'}")
    click.echo(f"Version: {h.version or 'unknown'}")
    click.echo(f"Provider: {h.provider or 'not configured'}")

    if h.details:
        click.echo("Details:")
        for k, v in h.details.items():
            click.echo(f"  {k}: {v}")
    if h.warnings:
        click.echo("Warnings:")
        for w in h.warnings:
            click.echo(f"  ⚠ {w}")


@main.command()
def backends():
    """List all registered local backends."""
    from turboflow_adapter.registry import registry

    for b in registry.list_all():
        click.echo(f"{b.id} — {b.name} ({b.license})")
        click.echo(f"  {b.description}")
        click.echo()


@main.command()
@click.argument("backend_id")
def install(backend_id):
    """Install a local agent backend."""
    from turboflow_adapter.registry import registry

    backend = registry.get(backend_id)
    try:
        _run(backend.install())
        click.echo(f"✓ {backend.name} installed")
    except Exception as e:
        click.echo(f"✗ {e}", err=True)
        sys.exit(1)


@main.command("resolve-model")
@click.argument("model")
@click.option("-b", "--backend", help="Backend to resolve for")
def resolve_model(model, backend):
    """Resolve a model tier name to a backend-specific string."""
    adapter = AgentAdapter(backend)
    click.echo(adapter.resolve_model(model))


# ── MCP ──────────────────────────────────────────────────────────────────


@main.group()
def mcp():
    """Manage MCP servers."""
    pass


@mcp.command("add")
@click.argument("name")
@click.argument("command")
@click.argument("args", nargs=-1)
def mcp_add(name, command, args):
    """Register an MCP server."""
    from turboflow_adapter.types import McpServer

    adapter = AgentAdapter()
    _run(adapter.mcp_add(McpServer(name=name, command=command, args=list(args) if args else None)))


@mcp.command("remove")
@click.argument("name")
def mcp_remove(name):
    """Remove an MCP server."""
    adapter = AgentAdapter()
    _run(adapter.mcp_remove(name))


@mcp.command("list")
def mcp_list():
    """List registered MCP servers."""
    adapter = AgentAdapter()
    servers = _run(adapter.mcp_list())
    if not servers:
        click.echo("No MCP servers registered")
        return
    for s in servers:
        args_str = " ".join(s.args) if s.args else ""
        click.echo(f"  {s.name}: {s.command} {args_str}")


if __name__ == "__main__":
    main()
