#!/usr/bin/env bash
# =============================================================================
# TurboFlow Agent Adapter — Shell Integration
#
# Auto-detects Python or TypeScript runtime and routes agent-* commands
# to the appropriate adapter. Python is preferred (Strands native support).
#
# Usage:
#   source agent-adapter/shell-integration.sh
# =============================================================================

# ── Locate adapter directory ────────────────────────────────────────────────
_TF_ADAPTER_DIR=""
if [ -n "${BASH_SOURCE[0]:-}" ]; then
    _TF_ADAPTER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
elif [ -n "${WORKSPACE:-}" ] && [ -d "${WORKSPACE}/agent-adapter" ]; then
    _TF_ADAPTER_DIR="${WORKSPACE}/agent-adapter"
fi

# ── Runtime detection ───────────────────────────────────────────────────────
# Prefer Python (Strands native), fall back to TypeScript
_TF_ADAPTER_RUNTIME=""

if [ -n "$_TF_ADAPTER_DIR" ]; then
    if [ -f "$_TF_ADAPTER_DIR/python/turboflow_adapter/cli.py" ] && command -v python3 &>/dev/null; then
        _TF_ADAPTER_RUNTIME="python"
    elif [ -f "$_TF_ADAPTER_DIR/ts/dist/cli.js" ] && command -v node &>/dev/null; then
        _TF_ADAPTER_RUNTIME="typescript"
    fi
fi

_tf_adapter() {
    case "$_TF_ADAPTER_RUNTIME" in
        python)
            python3 -m turboflow_adapter.cli "$@"
            ;;
        typescript)
            node "$_TF_ADAPTER_DIR/ts/dist/cli.js" "$@"
            ;;
        *)
            echo "Error: Agent adapter not found. Install Python or build TypeScript adapter." >&2
            return 1
            ;;
    esac
}

# ── Public shell functions ──────────────────────────────────────────────────

agent-exec()          { _tf_adapter exec "$@"; }
agent-status()        { _tf_adapter status; }
agent-health()        { _tf_adapter health "$@"; }
agent-switch()        { _tf_adapter switch "$@"; }
agent-install()       { _tf_adapter install "$@"; }
agent-backends()      { _tf_adapter backends; }
agent-version()       { _tf_adapter agent-version 2>/dev/null || _tf_adapter --version; }
agent-mcp-add()       { _tf_adapter mcp add "$@"; }
agent-mcp-remove()    { _tf_adapter mcp remove "$@"; }
agent-mcp-list()      { _tf_adapter mcp list; }
agent-resolve-model() { _tf_adapter resolve-model "$@"; }

export TURBOFLOW_AGENT_BACKEND="${TURBOFLOW_AGENT_BACKEND:-claude}"
export _TF_ADAPTER_RUNTIME
