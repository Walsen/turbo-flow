"""Aider backend — wraps the `aider` CLI."""

from __future__ import annotations

import os

from turboflow_adapter.backend import AgentBackend
from turboflow_adapter.process import run, command_exists
from turboflow_adapter.types import (
    BackendCapabilities,
    ExecOptions,
    ExecResult,
    HealthCheckResult,
)


class AiderBackend(AgentBackend):
    def __init__(self) -> None:
        super().__init__("aider")

    @property
    def name(self) -> str:
        return "Aider"

    @property
    def description(self) -> str:
        return "AI pair programming CLI with multi-model support (Apache 2.0)"

    @property
    def url(self) -> str:
        return "https://aider.chat"

    @property
    def license(self) -> str:
        return "Apache-2.0"

    @property
    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            multi_model=True,
            interactive=True,
            headless=True,
            streaming=True,
            bedrock=True,
            worktrees=True,
        )

    def resolve_model(self, model: str) -> str:
        is_bedrock = os.environ.get("CLAUDE_CODE_USE_BEDROCK") == "1"
        tier_map = {
            "opus": (
                f"bedrock/{os.environ.get('ANTHROPIC_DEFAULT_OPUS_MODEL', 'us.anthropic.claude-opus-4-6-v1')}",
                "claude-3-opus-20240229",
            ),
            "sonnet": (
                f"bedrock/{os.environ.get('ANTHROPIC_DEFAULT_SONNET_MODEL', 'us.anthropic.claude-sonnet-4-6')}",
                "claude-sonnet-4-20250514",
            ),
            "haiku": (
                f"bedrock/{os.environ.get('ANTHROPIC_DEFAULT_HAIKU_MODEL', 'us.anthropic.claude-haiku-4-5-20251001-v1:0')}",
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
        if opts.files:
            args.extend(opts.files)
        if opts.headless or opts.print_only:
            args.extend(["--message", prompt, "--no-auto-commits", "--yes"])
        args.extend(opts.extra_args or [])

        return run(
            "aider", args=args, cwd=opts.cwd, env=opts.env, timeout=opts.timeout, stream=True
        )

    async def version(self) -> str | None:
        result = run("aider", args=["--version"], timeout=10)
        return result.stdout.strip() if result.exit_code == 0 else None

    async def is_installed(self) -> bool:
        return command_exists("aider")

    async def health_check(self) -> HealthCheckResult:
        installed = await self.is_installed()
        ver = await self.version() if installed else None
        warnings: list[str] = []
        details: dict[str, str | bool] = {}

        providers = []
        if os.environ.get("ANTHROPIC_API_KEY"):
            providers.append("Anthropic")
        if os.environ.get("OPENAI_API_KEY"):
            providers.append("OpenAI")
        if os.environ.get("CLAUDE_CODE_USE_BEDROCK") == "1":
            providers.append("Bedrock")
        if not providers:
            warnings.append("No model provider configured")

        details["providers"] = ", ".join(providers) or "none"
        return HealthCheckResult(
            installed=installed,
            version=ver,
            provider=providers[0] if providers else None,
            details=details,
            warnings=warnings,
        )

    async def install(self) -> None:
        self.log.info("Installing Aider...")
        if command_exists("pipx"):
            result = run("pipx", args=["install", "aider-chat"], timeout=120, stream=True)
            if result.exit_code == 0:
                return
        pip = "pip3" if command_exists("pip3") else "pip"
        result = run(pip, args=["install", "--user", "aider-chat"], timeout=120, stream=True)
        if result.exit_code != 0:
            raise RuntimeError("Aider installation failed. Try: pipx install aider-chat")
