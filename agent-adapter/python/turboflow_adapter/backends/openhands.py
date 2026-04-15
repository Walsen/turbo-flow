"""OpenHands backend — wraps the OpenHands CLI or Docker container."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from turboflow_adapter.backend import AgentBackend
from turboflow_adapter.process import run, command_exists
from turboflow_adapter.types import (
    BackendCapabilities,
    ExecOptions,
    ExecResult,
    HealthCheckResult,
    McpServer,
)

DEFAULT_IMAGE = "ghcr.io/all-hands-ai/openhands:latest"


class OpenHandsBackend(AgentBackend):
    def __init__(self) -> None:
        super().__init__("openhands")
        self._image = os.environ.get("OPENHANDS_IMAGE", DEFAULT_IMAGE)

    @property
    def name(self) -> str:
        return "OpenHands"

    @property
    def description(self) -> str:
        return "Open-source AI software engineer (MIT license)"

    @property
    def url(self) -> str:
        return "https://github.com/All-Hands-AI/OpenHands"

    @property
    def license(self) -> str:
        return "MIT"

    @property
    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            mcp=True, multi_model=True, headless=True, streaming=True, worktrees=True
        )

    def resolve_model(self, model: str) -> str:
        tier_map = {
            "opus": "anthropic/claude-opus-4-20250514",
            "sonnet": "anthropic/claude-sonnet-4-20250514",
            "haiku": "anthropic/claude-haiku-4-5-20251001",
        }
        return tier_map.get(model, model)

    def _detect_api_key(self, model: str) -> str | None:
        if key := os.environ.get("LLM_API_KEY"):
            return key
        if model.startswith("anthropic/"):
            return os.environ.get("ANTHROPIC_API_KEY")
        if model.startswith("openai/"):
            return os.environ.get("OPENAI_API_KEY")
        return os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")

    async def exec(self, prompt: str, options: ExecOptions | None = None) -> ExecResult:
        opts = options or ExecOptions()
        model = (
            self.resolve_model(opts.model)
            if opts.model
            else os.environ.get("LLM_MODEL", "anthropic/claude-sonnet-4-20250514")
        )
        api_key = self._detect_api_key(model)
        if not api_key:
            return ExecResult(exit_code=1, stdout="", stderr="No API key found", duration_ms=0)

        full_prompt = prompt
        if opts.files:
            full_prompt = f"Focus on these files: {', '.join(opts.files)}. {prompt}"

        env = {"LLM_MODEL": model, "LLM_API_KEY": api_key, **(opts.env or {})}

        if command_exists("openhands"):
            return run(
                "openhands",
                args=["run", "--task", full_prompt],
                cwd=opts.cwd,
                env=env,
                timeout=opts.timeout,
                stream=True,
            )

        if command_exists("docker"):
            cwd = opts.cwd or os.getcwd()
            return run(
                "docker",
                args=[
                    "run",
                    "--rm",
                    "-e",
                    f"LLM_MODEL={model}",
                    "-e",
                    f"LLM_API_KEY={api_key}",
                    "-v",
                    f"{cwd}:/workspace:rw",
                    self._image,
                    "python",
                    "-m",
                    "openhands.core.main",
                    "-t",
                    full_prompt,
                ],
                timeout=opts.timeout,
                stream=True,
            )

        return ExecResult(
            exit_code=1, stdout="", stderr="Neither openhands CLI nor Docker found", duration_ms=0
        )

    async def version(self) -> str | None:
        if command_exists("openhands"):
            result = run("openhands", args=["--version"], timeout=10)
            return result.stdout.strip() if result.exit_code == 0 else None
        return None

    async def is_installed(self) -> bool:
        return command_exists("openhands") or command_exists("docker")

    async def health_check(self) -> HealthCheckResult:
        installed = await self.is_installed()
        ver = await self.version() if installed else None
        warnings: list[str] = []
        details: dict[str, str | bool] = {
            "cli": command_exists("openhands"),
            "docker": command_exists("docker"),
        }
        if (
            not os.environ.get("ANTHROPIC_API_KEY")
            and not os.environ.get("OPENAI_API_KEY")
            and not os.environ.get("LLM_API_KEY")
        ):
            warnings.append("No API key set")
        return HealthCheckResult(
            installed=installed, version=ver, provider=None, details=details, warnings=warnings
        )

    async def install(self) -> None:
        self.log.info("Installing OpenHands...")
        pip = "pip3" if command_exists("pip3") else "pip"
        result = run(pip, args=["install", "--user", "openhands"], timeout=180, stream=True)
        if result.exit_code == 0:
            return
        if command_exists("docker"):
            result = run("docker", args=["pull", self._image], timeout=300, stream=True)
            if result.exit_code == 0:
                return
        raise RuntimeError("OpenHands installation failed")

    # ── MCP via config file ──────────────────────────────────────────────

    @property
    def _mcp_config_path(self) -> Path:
        return Path.home() / ".openhands" / "mcp_servers.json"

    def _read_mcp_config(self) -> dict[str, Any]:
        try:
            if self._mcp_config_path.exists():
                result: dict[str, Any] = json.loads(self._mcp_config_path.read_text())
                return result
        except Exception:
            pass
        return {}

    def _write_mcp_config(self, config: dict[str, Any]) -> None:
        self._mcp_config_path.parent.mkdir(parents=True, exist_ok=True)
        self._mcp_config_path.write_text(json.dumps(config, indent=2))

    async def mcp_add(self, server: McpServer) -> None:
        config = self._read_mcp_config()
        config[server.name] = {"command": server.command, "args": server.args}
        self._write_mcp_config(config)
        self.log.info("MCP server '%s' registered (openhands)", server.name)

    async def mcp_remove(self, name: str) -> None:
        config = self._read_mcp_config()
        config.pop(name, None)
        self._write_mcp_config(config)
