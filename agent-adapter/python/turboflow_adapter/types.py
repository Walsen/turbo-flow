"""Core types for the Agent Adapter."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

BackendId = Literal["claude", "aider", "openhands", "strands"]


@dataclass
class BackendCapabilities:
    """What a backend can do."""

    mcp: bool = False
    agent_teams: bool = False
    multi_model: bool = False
    interactive: bool = False
    headless: bool = False
    streaming: bool = False
    bedrock: bool = False
    worktrees: bool = False
    otel: bool = False
    a2a: bool = False


@dataclass
class ExecOptions:
    """Options for agent execution."""

    files: list[str] | None = None
    model: str | None = None
    headless: bool = False
    print_only: bool = False
    cwd: str | None = None
    env: dict[str, str] | None = None
    timeout: float | None = None
    extra_args: list[str] | None = None
    system_prompt: str | None = None


@dataclass
class ExecResult:
    """Result from agent execution."""

    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    timed_out: bool = False


@dataclass
class McpServer:
    """MCP server registration info."""

    name: str
    command: str
    args: list[str] | None = None
    env: dict[str, str] | None = None


@dataclass
class HealthCheckResult:
    """Health check result."""

    installed: bool
    version: str | None
    provider: str | None
    details: dict[str, str | bool] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


@dataclass
class BackendInfo:
    """Backend metadata."""

    id: str
    name: str
    description: str
    url: str
    license: str
    capabilities: BackendCapabilities
    installed: bool = False
    version: str | None = None
    active: bool = False
