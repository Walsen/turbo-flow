"""
TurboFlow-specific tools for Strands agents.

These tools give Strands agents access to TurboFlow's unique capabilities:
- Beads (cross-session memory)
- File operations (read, write, list)
- Shell execution
"""

from __future__ import annotations

import os
import subprocess

from turboflow_adapter.logger import get_logger

log = get_logger("tf-adapter.strands.tools")

# We only define tools if Strands is available
try:
    from strands import tool as strands_tool

    _HAS_STRANDS = True
except ImportError:
    _HAS_STRANDS = False

    # Dummy decorator so the module loads without strands
    def strands_tool(fn=None, **kwargs):  # type: ignore
        def wrapper(f):
            return f

        return wrapper(fn) if fn else wrapper


# ── Beads tools (cross-session memory) ───────────────────────────────────


@strands_tool(
    name="beads_ready",
    description="Check project state — open tasks, blockers, in-progress work. Run this at the start of every session.",
)
def beads_ready() -> str:
    """Check Beads project state."""
    try:
        result = subprocess.run(
            ["bd", "ready", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout if result.returncode == 0 else f"Beads error: {result.stderr}"
    except FileNotFoundError:
        return "Beads (bd) not installed. Install with: npm i -g @beads/bd"
    except Exception as e:
        return f"Beads error: {e}"


@strands_tool(
    name="beads_create",
    description="Create a new Beads issue to track work. Types: bug, feature, task, epic, chore, decision. Priorities: 0 (critical) to 4 (backlog).",
)
def beads_create(title: str, type: str = "task", priority: int = 2, description: str = "") -> str:
    """Create a Beads issue."""
    try:
        args = ["bd", "create", title, "-t", type, "-p", str(priority), "--json"]
        if description:
            args.extend(["--description", description])
        result = subprocess.run(args, capture_output=True, text=True, timeout=10)
        return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
    except Exception as e:
        return f"Beads error: {e}"


@strands_tool(
    name="beads_close",
    description="Close a completed Beads issue with a reason explaining what was done and proof it works.",
)
def beads_close(id: str, reason: str) -> str:
    """Close a Beads issue."""
    try:
        result = subprocess.run(
            ["bd", "close", id, "--reason", reason, "--json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
    except Exception as e:
        return f"Beads error: {e}"


@strands_tool(
    name="beads_remember",
    description="Store a persistent key-value memory in Beads. Use for lessons learned, patterns, and decisions.",
)
def beads_remember(key: str, value: str) -> str:
    """Store persistent memory."""
    try:
        result = subprocess.run(
            ["bd", "remember", key, value],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
    except Exception as e:
        return f"Beads error: {e}"


# ── File tools ───────────────────────────────────────────────────────────


@strands_tool(name="read_file", description="Read the contents of a file.")
def read_file(path: str) -> str:
    """Read a file."""
    try:
        with open(path) as f:
            return f.read()
    except Exception as e:
        return f"Error reading {path}: {e}"


@strands_tool(
    name="write_file", description="Write content to a file. Creates the file if it doesn't exist."
)
def write_file(path: str, content: str) -> str:
    """Write a file."""
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return f"Written: {path}"
    except Exception as e:
        return f"Error writing {path}: {e}"


@strands_tool(name="list_directory", description="List files and directories at the given path.")
def list_directory(path: str = ".") -> str:
    """List directory contents."""
    try:
        entries = sorted(os.listdir(path))
        return "\n".join(entries) if entries else "(empty directory)"
    except Exception as e:
        return f"Error listing {path}: {e}"


@strands_tool(
    name="run_command",
    description="Run a shell command and return its output. Use non-interactive flags (e.g. -y, -f) to avoid hangs.",
)
def run_command(command: str, cwd: str | None = None) -> str:
    """Run a shell command."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=cwd,
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\nExit code: {result.returncode}"
        return output
    except subprocess.TimeoutExpired:
        return "Command timed out after 60s"
    except Exception as e:
        return f"Error: {e}"


# ── Tool collections ─────────────────────────────────────────────────────


def beads_tools() -> list:
    """Get all Beads-related tools."""
    if not _HAS_STRANDS:
        return []
    return [beads_ready, beads_create, beads_close, beads_remember]


def file_tools() -> list:
    """Get file operation tools."""
    if not _HAS_STRANDS:
        return []
    return [read_file, write_file, list_directory, run_command]


def all_tools() -> list:
    """Get all TurboFlow tools (Beads + file ops + GitNexus CLI + AgentDB memory)."""
    from turboflow_adapter.strands.gitnexus import gitnexus_cli_tools
    from turboflow_adapter.strands.memory import memory_tools

    return beads_tools() + file_tools() + gitnexus_cli_tools() + memory_tools()
