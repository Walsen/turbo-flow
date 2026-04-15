"""Process runner with timeout, streaming, and structured results."""

from __future__ import annotations

import os
import shutil
import subprocess
import time

from turboflow_adapter.logger import get_logger
from turboflow_adapter.types import ExecResult

log = get_logger("tf-adapter.process")


def run(
    command: str,
    args: list[str] | None = None,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    timeout: float | None = None,
    stdin_data: str | None = None,
    stream: bool = False,
) -> ExecResult:
    """Run a command and return structured result."""
    full_args = [command] + (args or [])
    merged_env = {**os.environ, **(env or {})}
    start = time.monotonic()

    log.debug("Spawning: %s", " ".join(full_args))

    try:
        proc = subprocess.run(
            full_args,
            cwd=cwd,
            env=merged_env,
            input=stdin_data,
            capture_output=not stream,
            text=True,
            timeout=timeout,
        )
        duration_ms = (time.monotonic() - start) * 1000

        return ExecResult(
            exit_code=proc.returncode,
            stdout=proc.stdout or "",
            stderr=proc.stderr or "",
            duration_ms=duration_ms,
            timed_out=False,
        )
    except subprocess.TimeoutExpired:
        duration_ms = (time.monotonic() - start) * 1000
        return ExecResult(
            exit_code=1,
            stdout="",
            stderr=f"Command timed out after {timeout}s",
            duration_ms=duration_ms,
            timed_out=True,
        )
    except FileNotFoundError:
        duration_ms = (time.monotonic() - start) * 1000
        return ExecResult(
            exit_code=1,
            stdout="",
            stderr=f"Command not found: {command}",
            duration_ms=duration_ms,
            timed_out=False,
        )


def command_exists(cmd: str) -> bool:
    """Check if a command exists on PATH."""
    return shutil.which(cmd) is not None
