"""Kiro CLI backend — wraps the `kiro` CLI.

AWS-native agentic coding CLI (evolved from Amazon Q Developer CLI).
Supports headless mode, Bedrock native, spec-driven development.
Eliminates Claude Code proprietary binary dependency for interactive terminal use.
"""

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


class KiroBackend(AgentBackend):
    def __init__(self) -> None:
        super().__init__("kiro")

    @property
    def name(self) -> str:
        return "Kiro CLI"

    @property
    def description(self) -> str:
        return "AWS-native agentic coding CLI with specs, hooks, and Bedrock support"

    @property
    def url(self) -> str:
        return "https://kiro.dev/cli/"

    @property
    def license(self) -> str:
        return "Proprietary (AWS)"

    @property
    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            mcp=True,
            agent_teams=False,
            multi_model=True,
            interactive=True,
            headless=True,
            streaming=True,
            bedrock=True,
            worktrees=True,
        )

    def resolve_model(self, model: str) -> str:
        # Kiro uses Bedrock model IDs natively
        is_bedrock = os.environ.get("CLAUDE_CODE_USE_BEDROCK") == "1"
        tier_map = {
            "opus": (
                os.environ.get("ANTHROPIC_DEFAULT_OPUS_MODEL", "us.anthropic.claude-opus-4-6-v1"),
                "claude-opus-4-20250514",
            ),
            "sonnet": (
                os.environ.get("ANTHROPIC_DEFAULT_SONNET_MODEL", "us.anthropic.claude-sonnet-4-6"),
                "claude-sonnet-4-20250514",
            ),
            "haiku": (
                os.environ.get(
                    "ANTHROPIC_DEFAULT_HAIKU_MODEL",
                    "us.anthropic.claude-haiku-4-5-20251001-v1:0",
                ),
                "claude-haiku-4-5-20251001",
            ),
        }
        tier = tier_map.get(model)
        if tier:
            return tier[0] if is_bedrock else tier[1]
        return model

    async def exec(self, prompt: str, options: ExecOptions | None = None) -> ExecResult:
        opts = options or ExecOptions()
        args: list[str] = []

        if opts.model:
            args.extend(["--model", self.resolve_model(opts.model)])

        if opts.headless or opts.print_only:
            args.append("--print")

        args.append(prompt)

        return run(
            "kiro",
            args=args,
            cwd=opts.cwd,
            env=opts.env,
            timeout=opts.timeout,
            stream=True,
        )

    async def version(self) -> str | None:
        result = run("kiro", args=["--version"], timeout=10)
        return result.stdout.strip() if result.exit_code == 0 else None

    async def is_installed(self) -> bool:
        return command_exists("kiro")

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
            details["provider"] = "Anthropic API"
        else:
            details["provider"] = "not configured"
            warnings.append("No auth configured")

        if not installed:
            warnings.append("Kiro CLI not installed. Visit: https://kiro.dev/cli/")

        return HealthCheckResult(
            installed=installed,
            version=ver,
            provider=str(details.get("provider")),
            details=details,
            warnings=warnings,
        )

    async def install(self) -> None:
        self.log.info("Installing Kiro CLI...")
        # Kiro CLI install — check if there's a standard installer
        result = run(
            "bash",
            args=["-c", "curl -fsSL https://kiro.dev/install.sh | bash"],
            timeout=120,
            stream=True,
        )
        if result.exit_code == 0 and command_exists("kiro"):
            self.log.info("Kiro CLI installed")
            return
        # Fallback: npm
        result = run("npm", args=["install", "-g", "@anthropic-ai/kiro"], timeout=120, stream=True)
        if result.exit_code == 0:
            self.log.info("Kiro CLI installed (npm)")
            return
        raise RuntimeError("Kiro CLI installation failed. Visit: https://kiro.dev/cli/")

    async def mcp_add(self, server: McpServer) -> None:
        args = ["mcp", "add", server.name, "--", server.command]
        if server.args:
            args.extend(server.args)
        result = run("kiro", args=args, timeout=15)
        if result.exit_code == 0:
            self.log.info("MCP server '%s' registered (kiro)", server.name)

    async def mcp_remove(self, name: str) -> None:
        run("kiro", args=["mcp", "remove", name], timeout=10)
