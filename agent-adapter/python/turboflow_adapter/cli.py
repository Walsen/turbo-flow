"""CLI entry point for the Agent Adapter."""

from __future__ import annotations

import asyncio
import sys

import click

from turboflow_adapter.adapter import AgentAdapter
from turboflow_adapter.types import ExecOptions


def _run(coro):
    """Run an async function synchronously."""
    return asyncio.run(coro)


@click.group()
@click.version_option(version="0.1.0")
def main():
    """TurboFlow Agent Adapter — provider-independent agent CLI abstraction."""
    pass


@main.command()
@click.argument("prompt")
@click.option("-f", "--file", "files", multiple=True, help="Target file(s)")
@click.option("-m", "--model", help="Model override (opus/sonnet/haiku or backend-specific)")
@click.option("--headless", is_flag=True, help="Non-interactive mode")
@click.option("--print", "print_only", is_flag=True, help="Print-only mode")
@click.option("-b", "--backend", help="Override backend for this command")
@click.option("-t", "--timeout", type=float, help="Timeout in seconds")
@click.option("-s", "--system-prompt", help="System prompt override")
def exec(prompt, files, model, headless, print_only, backend, timeout, system_prompt):
    """Execute a prompt through the active agent backend."""
    adapter = AgentAdapter(backend)
    result = _run(
        adapter.exec(
            prompt,
            ExecOptions(
                files=list(files) if files else None,
                model=model,
                headless=headless,
                print_only=print_only,
                timeout=timeout,
                system_prompt=system_prompt,
            ),
        )
    )
    if result.stdout:
        click.echo(result.stdout)
    if result.stderr:
        click.echo(result.stderr, err=True)
    sys.exit(result.exit_code)


@main.command()
def status():
    """Show status of all agent backends."""
    adapter = AgentAdapter()
    statuses = _run(adapter.status())

    click.echo("╔══════════════════════════════════════════╗")
    click.echo("║   TurboFlow Agent Adapter Status          ║")
    click.echo("╚══════════════════════════════════════════╝")
    click.echo()

    for s in statuses:
        active = " (active)" if s.active else ""
        icon = "✓" if s.installed else "✗"
        ver = f" — {s.version}" if s.version else ""
        click.echo(f"  {icon} {s.name}{active}{ver}")
        click.echo(f"    {s.description}")

        caps = [k for k, v in vars(s.capabilities).items() if v]
        click.echo(f"    Capabilities: {', '.join(caps)}")
        click.echo()


@main.command()
@click.option("-b", "--backend", help="Check a specific backend")
def health(backend):
    """Run health check on the active backend."""
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
@click.argument("backend_id")
def switch(backend_id):
    """Switch the active agent backend."""
    adapter = AgentAdapter()
    try:
        _run(adapter.switch_backend(backend_id))
        click.echo(f"✓ Switched to {backend_id}")
    except Exception as e:
        click.echo(f"✗ {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("backend_id")
def install(backend_id):
    """Install an agent backend."""
    from turboflow_adapter.registry import registry

    backend = registry.get(backend_id)
    try:
        _run(backend.install())
        click.echo(f"✓ {backend.name} installed")
    except Exception as e:
        click.echo(f"✗ {e}", err=True)
        sys.exit(1)


@main.command()
def backends():
    """List all registered backends."""
    from turboflow_adapter.registry import registry

    for b in registry.list_all():
        click.echo(f"{b.id} — {b.name} ({b.license})")
        click.echo(f"  {b.description}")
        click.echo(f"  {b.url}")
        click.echo()


@main.command("resolve-model")
@click.argument("model")
@click.option("-b", "--backend", help="Backend to resolve for")
def resolve_model(model, backend):
    """Resolve a model tier name to a backend-specific model string."""
    adapter = AgentAdapter(backend)
    click.echo(adapter.resolve_model(model))


# ── MCP subcommands ──────────────────────────────────────────────────────


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
