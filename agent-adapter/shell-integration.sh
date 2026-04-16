#!/usr/bin/env bash
# =============================================================================
# TurboFlow — Shell Integration
#
# Provides the `tf` command and agent-* aliases.
# Auto-detects Python or TypeScript runtime. Python preferred (Strands native).
#
# Usage:
#   source agent-adapter/shell-integration.sh
#   tf "Write a fibonacci function"
# =============================================================================

# ── Locate adapter directory ────────────────────────────────────────────────
_TF_ADAPTER_DIR=""
if [ -n "${BASH_SOURCE[0]:-}" ]; then
    _TF_ADAPTER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
elif [ -n "${WORKSPACE:-}" ] && [ -d "${WORKSPACE}/agent-adapter" ]; then
    _TF_ADAPTER_DIR="${WORKSPACE}/agent-adapter"
fi

# ── Runtime detection ───────────────────────────────────────────────────────
_TF_ADAPTER_RUNTIME=""

if [ -n "$_TF_ADAPTER_DIR" ]; then
    if [ -f "$_TF_ADAPTER_DIR/python/turboflow_adapter/cli.py" ] && command -v python3 &>/dev/null; then
        _TF_ADAPTER_RUNTIME="python"
    elif [ -f "$_TF_ADAPTER_DIR/ts/dist/cli.js" ] && command -v node &>/dev/null; then
        _TF_ADAPTER_RUNTIME="typescript"
    fi
fi

_tf_cli() {
    case "$_TF_ADAPTER_RUNTIME" in
        python)
            python3 -m turboflow_adapter.cli "$@"
            ;;
        typescript)
            node "$_TF_ADAPTER_DIR/ts/dist/cli.js" "$@"
            ;;
        *)
            echo "Error: TurboFlow not found. Install Python adapter or build TypeScript adapter." >&2
            return 1
            ;;
    esac
}

# ── Main command ────────────────────────────────────────────────────────────

tf()                  { _tf_cli "$@"; }

# ── Aliases for discoverability ─────────────────────────────────────────────

agent-exec()          { _tf_cli "$@"; }
agent-status()        { _tf_cli status; }
agent-health()        { _tf_cli health "$@"; }
agent-backends()      { _tf_cli backends; }
agent-install()       { _tf_cli install "$@"; }
agent-mcp-add()       { _tf_cli mcp add "$@"; }
agent-mcp-remove()    { _tf_cli mcp remove "$@"; }
agent-mcp-list()      { _tf_cli mcp list; }
agent-resolve-model() { _tf_cli resolve-model "$@"; }

export TURBOFLOW_AGENT_BACKEND="${TURBOFLOW_AGENT_BACKEND:-claude}"
export _TF_ADAPTER_RUNTIME
