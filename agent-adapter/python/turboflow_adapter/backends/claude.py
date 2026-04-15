"""Claude Code backend — wraps the `claude` CLI."""

from __future__ import annotations

import os

from turboflow_adapter.backend import AgentBackend
from turboflow_adapter.process import run, command_exists
from turboflow_adapter.types import (
    BackendCapabilities,
    ExecOptions,
    ExecResult,
    HealthCheckResult,
    McpServer,
)

_TIER_MAP = {
    "opus": {
        "bedrock": lambda: os.environ.get(
            "ANTHROPIC_DEFAULT_OPUS_MODEL", "us.anthropic.claude-opus-4-6-v1"
        ),
        "direct": "claude-opus-4-20250514",
    },
    "sonnet": {
        "bedrock": lambda: os.environ.get(
            "ANTHROPIC_DEFAULT_SONNET_MODEL", "us.anthropic.claude-sonnet-4-6"
        ),
        "direct": "claude-sonnet-4-20250514",
    },
    "haiku": {
        "bedrock": lambda: os.environ.get(
            "ANTHROPIC_DEFAULT_HAIKU_MODEL", "us.anthropic.claude-haiku-4-5-20251001-v1:0"
        ),
        "direct": "claude-haiku-4-5-20251001",
    },
}


class ClaudeBackend(AgentBackend):
    def __init__(self) -> None:
        super().__init__("claude")

    @property
    def name(self) -> str:
        return "Claude Code"

    @property
    def description(self) -> str:
        return "Anthropic's agentic coding CLI with MCP, Agent Teams, and Bedrock support"

    @property
    def url(self) -> str:
        return "https://claude.ai/code"

    @property
    def license(self) -> str:
        return "Proprietary"

    @property
    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            mcp=True,
            agent_teams=True,
            interactive=True,
            headless=True,
            streaming=True,
            bedrock=True,
            worktrees=True,
        )

    def resolve_model(self, model: str) -> str:
        tier = _TIER_MAP.get(model)
        if not tier:
            return model
        if os.environ.get("CLAUDE_CODE_USE_BEDROCK") == "1":
            resolver = tier["bedrock"]
            return str(resolver()) if callable(resolver) else str(resolver)
        return str(tier["direct"])

    async def exec(self, prompt: str, options: ExecOptions | None = None) -> ExecResult:
        opts = options or ExecOptions()
        args: list[str] = []

        if opts.model:
            args.extend(["--model", self.resolve_model(opts.model)])
        if opts.print_only or opts.headless:
            args.append("--print")

        args.append(prompt)

        return run(
            "claude",
            args=args,
            cwd=opts.cwd,
            env=opts.env,
            timeout=opts.timeout,
            stream=True,
        )

    async def version(self) -> str | None:
        result = run("claude", args=["--version"], timeout=10)
        return result.stdout.strip() if result.exit_code == 0 else None

    async def is_installed(self) -> bool:
        return command_exists("claude")

    async def health_check(self) -> HealthCheckResult:
        installed = await self.is_installed()
        ver = await self.version() if installed else None
        warnings: list[str] = []
        details: dict[str, str | bool] = {}

        is_bedrock = os.environ.get("CLAUDE_CODE_USE_BEDROCK") == "1"
        if is_bedrock:
            details["provider"] = "Amazon Bedrock"
            details["region"] = os.environ.get("AWS_REGION", "us-east-1")
        elif os.environ.get("ANTHROPIC_API_KEY"):
            details["provider"] = "Anthropic API (direct)"
        else:
            details["provider"] = "not configured"
            warnings.append("No auth configured")

        details["agent_teams"] = os.environ.get("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS") == "1"
        return HealthCheckResult(
            installed=installed,
            version=ver,
            provider=str(details.get("provider")),
            details=details,
            warnings=warnings,
        )

    async def install(self) -> None:
        self.log.info("Installing Claude Code...")
        result = run(
            "bash",
            args=["-c", "curl -fsSL https://claude.ai/install.sh | bash"],
            timeout=120,
            stream=True,
        )
        if result.exit_code == 0 and command_exists("claude"):
            self.log.info("Claude Code installed (native)")
            return
        result = run(
            "npm", args=["install", "-g", "@anthropic-ai/claude-code"], timeout=120, stream=True
        )
        if result.exit_code == 0:
            self.log.info("Claude Code installed (npm)")
            return
        raise RuntimeError("Claude Code installation failed")

    async def mcp_add(self, server: McpServer) -> None:
        args = ["mcp", "add", server.name, "--", server.command]
        if server.args:
            args.extend(server.args)
        result = run("claude", args=args, timeout=15)
        if result.exit_code == 0:
            self.log.info("MCP server '%s' registered", server.name)

    async def mcp_remove(self, name: str) -> None:
        run("claude", args=["mcp", "remove", name], timeout=10)
