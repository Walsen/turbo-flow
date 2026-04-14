#!/usr/bin/env bash
# =============================================================================
# TurboFlow 4.0 — Universal Bootstrap
#
# The only entry point you need. Installs the Task runner (single static
# binary, ~7MB, zero runtime deps) then delegates everything to Taskfile.yml.
#
# This script lives inside devpods/ and is designed to work after the standard
# TurboFlow install pattern:
#   git clone <repo> → cp -r repo/devpods . → rm -rf repo → bash devpods/bootstrap.sh
#
# It also works when run directly from the cloned repo:
#   cd turbo-flow-claude && bash devpods/bootstrap.sh
#
# Or as a one-liner (remote bootstrap):
#   curl -fsSL <repo-raw>/devpods/bootstrap.sh | bash
#
# Works on: Linux, macOS, Codespaces, DevPod, Rackspace K8s, Cloud Shell, Docker
# Requires: bash, curl, git (present on all targets)
# =============================================================================
set -euo pipefail

BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "  ${CYAN}→${NC} $1"; }
ok()    { echo -e "  ${GREEN}✓${NC} $1"; }
warn()  { echo -e "  ${YELLOW}⚠${NC} $1"; }
fail()  { echo -e "  ${RED}✗${NC} $1"; exit 1; }

echo -e "${BOLD}"
echo "╔══════════════════════════════════════════════════╗"
echo "║       🚀 TurboFlow 4.0 — Bootstrap               ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# ── Locate devpods directory ─────────────────────────────────────────────────
# Works whether called as:
#   bash devpods/bootstrap.sh          (from workspace root)
#   bash bootstrap.sh                  (from inside devpods/)
#   curl ... | bash                    (piped, no BASH_SOURCE)
SCRIPT_DIR=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ "${BASH_SOURCE[0]}" != "bash" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

# Determine workspace root (parent of devpods/)
if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/Taskfile.yml" ]; then
    # Script is inside devpods/ and Taskfile.yml is alongside it
    DEVPODS_DIR="$SCRIPT_DIR"
    WORKSPACE="$(dirname "$SCRIPT_DIR")"
elif [ -d "devpods" ] && [ -f "devpods/Taskfile.yml" ]; then
    # Called from workspace root
    DEVPODS_DIR="$(pwd)/devpods"
    WORKSPACE="$(pwd)"
elif [ -f "Taskfile.yml" ] && [ -f "setup.sh" ]; then
    # Called from inside devpods/ directly
    DEVPODS_DIR="$(pwd)"
    WORKSPACE="$(dirname "$(pwd)")"
else
    # Remote bootstrap — need to clone first
    info "Cloning turbo-flow repository..."
    WORKSPACE="${WORKSPACE:-$(pwd)}"
    CLONE_DIR=$(mktemp -d)
    git clone --depth 1 https://github.com/adventurewavelabs/turbo-flow "$CLONE_DIR/turbo-flow-claude"

    if [ ! -d "$CLONE_DIR/turbo-flow-claude/devpods" ]; then
        rm -rf "$CLONE_DIR"
        fail "devpods/ not found in cloned repo"
    fi

    # Standard pattern: copy devpods to workspace, delete clone
    cp -r "$CLONE_DIR/turbo-flow-claude/devpods" "$WORKSPACE/devpods"
    rm -rf "$CLONE_DIR"
    chmod +x "$WORKSPACE/devpods/"*.sh 2>/dev/null || true

    DEVPODS_DIR="$WORKSPACE/devpods"
    ok "devpods/ copied to $WORKSPACE"
fi

export WORKSPACE
export DEVPODS_DIR
info "Workspace: $WORKSPACE"
info "DevPods:   $DEVPODS_DIR"

# ── Install Task runner ──────────────────────────────────────────────────────
TASK_BIN_DIR="${HOME}/.local/bin"
mkdir -p "$TASK_BIN_DIR"
export PATH="${TASK_BIN_DIR}:${PATH}"

if ! command -v task &>/dev/null; then
    info "Installing Task runner..."

    if command -v brew &>/dev/null; then
        brew install go-task 2>/dev/null && ok "Task installed via Homebrew" || true
    fi

    if ! command -v task &>/dev/null; then
        curl -fsSL https://taskfile.dev/install.sh | sh -s -- -d -b "$TASK_BIN_DIR" 2>/dev/null
        ok "Task installed to $TASK_BIN_DIR"
    fi

    if ! command -v task &>/dev/null; then
        fail "Could not install Task runner. Install manually: https://taskfile.dev/installation/"
    fi
else
    ok "Task runner $(task --version 2>/dev/null | head -1) already present"
fi

# ── Parse arguments ──────────────────────────────────────────────────────────
TASK_TARGET="setup"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --task) TASK_TARGET="$2"; shift 2 ;;
        --) shift; break ;;
        *) TASK_TARGET="$1"; shift ;;
    esac
done

# ── Run from devpods/ where Taskfile.yml lives ───────────────────────────────
info "Running: task $TASK_TARGET"
echo ""

cd "$DEVPODS_DIR"
exec task "$TASK_TARGET"
