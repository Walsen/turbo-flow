"""
GitNexus integration for Strands agents.

Exposes GitNexus codebase intelligence as tools for Strands agents:
- query: hybrid search across the knowledge graph
- context: 360-degree symbol view (callers, callees, processes)
- impact: blast radius analysis before editing shared code
- detect_changes: git-diff impact mapping
- list_repos: discover indexed repositories

GitNexus runs as an MCP server (npx gitnexus mcp). Strands has native
MCP support, so we connect them directly.

For agents that can't use MCP, we also provide subprocess-based tool
wrappers that call the GitNexus CLI.
"""

from __future__ import annotations

import subprocess
from typing import Any

from turboflow_adapter.logger import get_logger

log = get_logger("tf-adapter.strands.gitnexus")

try:
    from strands import tool as strands_tool

    _HAS_STRANDS = True
except ImportError:
    _HAS_STRANDS = False

    def strands_tool(fn: Any = None, **kwargs: Any) -> Any:  # type: ignore
        def wrapper(f: Any) -> Any:
            return f

        return wrapper(fn) if fn else wrapper


def _run_gitnexus_mcp_tool(tool_name: str, args: dict[str, Any]) -> str:
    """Call a GitNexus MCP tool via the CLI's JSON output mode."""
    try:
        # GitNexus CLI can be invoked for individual operations
        cmd = ["npx", "-y", "gitnexus@latest"]

        if tool_name == "query":
            cmd.extend(["analyze", "--json"])  # fallback: re-analyze and query
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return f"GitNexus error: {result.stderr}"
            return result.stdout

        # For most tools, we use the MCP server via stdin/stdout
        # But since that requires a persistent connection, we use CLI fallbacks
        return f"Tool '{tool_name}' requires MCP connection. Use gitnexus_mcp_tools() with Strands MCP support."

    except FileNotFoundError:
        return "GitNexus not installed. Run: npm install -g gitnexus"
    except subprocess.TimeoutExpired:
        return "GitNexus command timed out"
    except Exception as e:
        return f"GitNexus error: {e}"


# ── Subprocess-based tools (work without MCP) ────────────────────────────


@strands_tool(
    name="gitnexus_analyze",
    description=(
        "Index the current repository with GitNexus to build a knowledge graph. "
        "Run this before using other GitNexus tools. Creates a graph of all "
        "dependencies, call chains, clusters, and execution flows."
    ),
)
def gitnexus_analyze(path: str = ".") -> str:
    """Index a repository with GitNexus."""
    try:
        result = subprocess.run(
            ["npx", "-y", "gitnexus@latest", "analyze", path],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            return f"Repository indexed successfully.\n{result.stdout}"
        return f"GitNexus analyze failed: {result.stderr}"
    except FileNotFoundError:
        return "GitNexus not installed. Run: npm install -g gitnexus"
    except subprocess.TimeoutExpired:
        return "GitNexus analyze timed out (>120s). Try a smaller repo or use --skip-embeddings."
    except Exception as e:
        return f"GitNexus error: {e}"


@strands_tool(
    name="gitnexus_status",
    description="Check the GitNexus index status for the current repository.",
)
def gitnexus_status(path: str = ".") -> str:
    """Check index status."""
    try:
        result = subprocess.run(
            ["npx", "-y", "gitnexus@latest", "status"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=path,
        )
        return result.stdout if result.returncode == 0 else f"Not indexed or error: {result.stderr}"
    except FileNotFoundError:
        return "GitNexus not installed."
    except Exception as e:
        return f"GitNexus error: {e}"


@strands_tool(
    name="gitnexus_list_repos",
    description="List all repositories that have been indexed by GitNexus.",
)
def gitnexus_list_repos() -> str:
    """List indexed repositories."""
    try:
        result = subprocess.run(
            ["npx", "-y", "gitnexus@latest", "list"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.stdout if result.returncode == 0 else "No repositories indexed."
    except FileNotFoundError:
        return "GitNexus not installed."
    except Exception as e:
        return f"GitNexus error: {e}"


@strands_tool(
    name="gitnexus_wiki",
    description=(
        "Generate documentation wiki from the GitNexus knowledge graph. "
        "Produces per-module documentation with cross-references."
    ),
)
def gitnexus_wiki(path: str = ".") -> str:
    """Generate wiki documentation."""
    try:
        result = subprocess.run(
            ["npx", "-y", "gitnexus@latest", "wiki", path],
            capture_output=True,
            text=True,
            timeout=120,
        )
        return (
            result.stdout if result.returncode == 0 else f"Wiki generation failed: {result.stderr}"
        )
    except FileNotFoundError:
        return "GitNexus not installed."
    except Exception as e:
        return f"GitNexus error: {e}"


# ── MCP-based tools (full power, requires MCP connection) ────────────────


def gitnexus_mcp_tools() -> list[Any]:
    """
    Get GitNexus tools via Strands MCP integration.

    This connects to the GitNexus MCP server and exposes all 7 tools
    (query, context, impact, detect_changes, rename, cypher, list_repos)
    natively through Strands' MCP support.

    Usage:
        from turboflow_adapter.strands.gitnexus import gitnexus_mcp_client
        from strands import Agent

        # Create MCP client (use as context manager)
        mcp = gitnexus_mcp_client()
        with mcp:
            agent = Agent(
                tools=[*mcp.list_tools_sync(), *other_tools],
                system_prompt="You have access to GitNexus codebase intelligence..."
            )
            result = agent("Analyze the blast radius of changing UserService")
    """
    try:
        client = gitnexus_mcp_client()
        client.start()
        tools = client.list_tools_sync()
        log.info("GitNexus MCP connected: %d tools available", len(tools))
        return list(tools)
    except ImportError:
        log.warning("Strands MCP support not available")
        return []
    except Exception as e:
        log.warning("GitNexus MCP connection failed: %s. Falling back to CLI tools.", e)
        return []


def gitnexus_mcp_client() -> Any:
    """
    Create a Strands MCPClient connected to the GitNexus MCP server.

    Returns an MCPClient that must be started before use:
        client = gitnexus_mcp_client()
        client.start()
        # ... use client.list_tools_sync() etc.
        client.stop()
    """
    from mcp import StdioServerParameters, stdio_client
    from strands.tools.mcp import MCPClient

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "gitnexus@latest", "mcp"],
    )

    return MCPClient(lambda: stdio_client(server_params))


# ── Tool collections ─────────────────────────────────────────────────────


def gitnexus_cli_tools() -> list[Any]:
    """Get GitNexus CLI-based tools (always available if npx is installed)."""
    if not _HAS_STRANDS:
        return []
    return [gitnexus_analyze, gitnexus_status, gitnexus_list_repos, gitnexus_wiki]


def gitnexus_tools(use_mcp: bool = False) -> list[Any]:
    """
    Get GitNexus tools for Strands agents.

    Args:
        use_mcp: If True, try to connect via MCP for full tool access
                 (query, context, impact, detect_changes, rename, cypher).
                 If False or MCP fails, fall back to CLI tools.
    """
    if use_mcp:
        mcp_tools = gitnexus_mcp_tools()
        if mcp_tools:
            return mcp_tools

    return gitnexus_cli_tools()
