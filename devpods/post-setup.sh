#!/bin/bash
# =============================================================================
# TurboFlow 4.0 Post-Setup Verification Script
# Replaces: post-setup.sh from v3.4.1
#
# Verifies and configures all components installed by setup-turboflow-4.sh:
#   - Claude Code + Ruflo v3.5
#   - 6 Ruflo plugins + OpenSpec
#   - GitNexus codebase knowledge graph
#   - Beads cross-session memory
#   - Native Agent Teams
#   - Statusline Pro
#   - CLAUDE.md + workspace + aliases
# =============================================================================

# Get the directory where this script is located
readonly DEVPOD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# PATH setup
if [ -n "$npm_config_prefix" ]; then
    export PATH="$npm_config_prefix/bin:$PATH"
elif [ -f "$HOME/.npmrc" ]; then
    _NPM_PREFIX=$(grep '^prefix=' "$HOME/.npmrc" 2>/dev/null | cut -d= -f2)
    [ -n "$_NPM_PREFIX" ] && export PATH="$_NPM_PREFIX/bin:$PATH"
fi
export PATH="$HOME/.local/bin:$HOME/.claude/bin:$PATH"

# Colors
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly RED='\033[0;31m'
readonly NC='\033[0m'

success() { echo -e "  ${GREEN}✓${NC} $*"; }
warning() { echo -e "  ${YELLOW}⚠${NC} $*"; }
fail()    { echo -e "  ${RED}✗${NC} $*"; }
info()    { echo -e "  ${BLUE}ℹ${NC} $*"; }
section() { echo -e "\n${CYAN}━━━ $* ━━━${NC}"; }

WORKSPACE="${WORKSPACE_FOLDER:=$(pwd)}"
ISSUES=0
PASS=0

track() {
    if "$@"; then
        ((PASS++))
    else
        ((ISSUES++))
    fi
}

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║      🔍 TurboFlow 4.0 Post-Setup Verify         ║"
echo "║   Ruflo v3.5 + Beads + Worktrees + Agent Teams  ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "  Workspace: $WORKSPACE"
echo ""

# =============================================================================
# STEP 1: Core Installations
# =============================================================================
section "Step 1: Core Installations"

# Build tools
if command -v g++ >/dev/null 2>&1 && command -v make >/dev/null 2>&1; then
    success "Build tools (g++, make)"
    ((PASS++))
else
    warning "Build tools not found"
    ((ISSUES++))
fi

# jq
if command -v jq >/dev/null 2>&1; then
    success "jq $(jq --version 2>/dev/null)"
    ((PASS++))
else
    warning "jq not found (needed for statusline)"
    ((ISSUES++))
fi

# Node.js
if command -v node >/dev/null 2>&1; then
    NODE_VER=$(node -v)
    NODE_MAJOR=$(echo "$NODE_VER" | sed 's/v//' | cut -d. -f1)
    if [ "$NODE_MAJOR" -ge 20 ]; then
        success "Node.js $NODE_VER"
        ((PASS++))
    else
        warning "Node.js $NODE_VER (v20+ required for Ruflo v3.5)"
        ((ISSUES++))
    fi
else
    fail "Node.js not found"
    ((ISSUES++))
fi

# Claude Code
if command -v claude >/dev/null 2>&1; then
    success "Claude Code $(claude --version 2>/dev/null | head -1)"
    ((PASS++))
else
    fail "Claude Code not found — run setup-turboflow-4.sh first"
    ((ISSUES++))
fi

# Ruflo
RF_VERSION=$(npx ruflo@latest --version 2>/dev/null | head -1 || echo "")
if [ -n "$RF_VERSION" ]; then
    success "Ruflo $RF_VERSION"
    ((PASS++))
else
    fail "Ruflo not responding — run: npx ruflo@latest init"
    ((ISSUES++))
fi

# =============================================================================
# STEP 2: Ruflo MCP + Doctor
# =============================================================================
section "Step 2: Ruflo MCP + Health Check"

# MCP registration
MCP_OK=false
for cfg in "$HOME/.config/claude/mcp.json" "$HOME/.claude/claude_desktop_config.json"; do
    if [ -f "$cfg" ] && grep -q "ruflo" "$cfg" 2>/dev/null; then
        MCP_OK=true
        break
    fi
done

if $MCP_OK; then
    success "Ruflo MCP server registered"
    ((PASS++))
else
    warning "Ruflo MCP not found in config — run: claude mcp add ruflo -- npx -y ruflo@latest"
    ((ISSUES++))
fi

# Check for stale claude-flow registration
for cfg in "$HOME/.config/claude/mcp.json" "$HOME/.claude/claude_desktop_config.json"; do
    if [ -f "$cfg" ] && grep -q "claude-flow" "$cfg" 2>/dev/null; then
        warning "Stale claude-flow MCP registration found in $cfg — run: claude mcp remove claude-flow"
        ((ISSUES++))
    fi
done

# Doctor
DOCTOR_OUTPUT=$(npx ruflo@latest doctor 2>&1 || true)
if echo "$DOCTOR_OUTPUT" | grep -qi "error\|failed\|critical"; then
    warning "Ruflo doctor found issues:"
    echo "$DOCTOR_OUTPUT" | head -10 | sed 's/^/    /'
    ((ISSUES++))
else
    success "Ruflo doctor passed"
    ((PASS++))
fi

# =============================================================================
# STEP 3: Ruflo Plugins
# =============================================================================
section "Step 3: Ruflo Plugins (6)"

PLUGIN_DIR="$WORKSPACE/.claude-flow/plugins"

check_plugin() {
    local name="$1"
    local display="$2"
    if [ -d "$PLUGIN_DIR/$name" ] && [ -f "$PLUGIN_DIR/$name/package.json" ]; then
        success "$display"
        ((PASS++))
    else
        warning "$display — not found (run: npx ruflo@latest plugins install -n $name)"
        ((ISSUES++))
    fi
}

check_plugin "@claude-flow/plugin-agentic-qe" "Agentic QE (58 QE agents, TDD, coverage)"
check_plugin "@claude-flow/plugin-code-intelligence" "Code Intelligence (analysis, patterns)"
check_plugin "@claude-flow/plugin-test-intelligence" "Test Intelligence (generation, gap analysis)"
check_plugin "@claude-flow/plugin-perf-optimizer" "Perf Optimizer (profiling, bottlenecks)"
check_plugin "@claude-flow/teammate-plugin" "Teammate Plugin (Agent Teams bridge, 21 MCP tools)"
check_plugin "@claude-flow/plugin-gastown-bridge" "Gastown Bridge (WASM orchestration, 20 MCP tools)"

# =============================================================================
# STEP 4: OpenSpec
# =============================================================================
section "Step 4: OpenSpec"

if npm list -g @fission-ai/openspec --depth=0 >/dev/null 2>&1; then
    success "OpenSpec installed globally"
    ((PASS++))
elif npx @fission-ai/openspec --version >/dev/null 2>&1; then
    success "OpenSpec available via npx"
    ((PASS++))
else
    warning "OpenSpec not installed — run: npm i -g @fission-ai/openspec"
    ((ISSUES++))
fi

# =============================================================================
# STEP 5: UI UX Pro Max Skill
# =============================================================================
section "Step 5: UI UX Pro Max Skill"

UIPRO_SKILL_DIR="$HOME/.claude/skills/ui-ux-pro-max"
UIPRO_SKILL_DIR_LOCAL="$WORKSPACE/.claude/skills/ui-ux-pro-max"

if [ -d "$UIPRO_SKILL_DIR" ] && [ -n "$(ls -A "$UIPRO_SKILL_DIR" 2>/dev/null)" ]; then
    success "UI UX Pro Max skill installed (global)"
    ((PASS++))
elif [ -d "$UIPRO_SKILL_DIR_LOCAL" ] && [ -n "$(ls -A "$UIPRO_SKILL_DIR_LOCAL" 2>/dev/null)" ]; then
    success "UI UX Pro Max skill installed (local)"
    ((PASS++))
else
    warning "UI UX Pro Max skill missing — run: npx uipro-cli init --ai claude"
    ((ISSUES++))
fi

# =============================================================================
# STEP 5: GitNexus
# =============================================================================
section "Step 6: GitNexus (Codebase Knowledge Graph)"

if command -v gitnexus >/dev/null 2>&1; then
    success "GitNexus installed globally"
    ((PASS++))
elif npx gitnexus --version >/dev/null 2>&1; then
    success "GitNexus available via npx"
    ((PASS++))
else
    warning "GitNexus not installed — run: npm i -g gitnexus"
    ((ISSUES++))
fi

# GitNexus MCP
GNX_MCP=false
for cfg in "$HOME/.config/claude/mcp.json" "$HOME/.claude/claude_desktop_config.json"; do
    if [ -f "$cfg" ] && grep -q "gitnexus" "$cfg" 2>/dev/null; then
        GNX_MCP=true
        break
    fi
done

if $GNX_MCP; then
    success "GitNexus MCP server registered"
    ((PASS++))
else
    warning "GitNexus MCP not registered — run: npx gitnexus setup"
    ((ISSUES++))
fi

# Workspace indexed?
if [ -d "$WORKSPACE/.git" ]; then
    if [ -d "$WORKSPACE/.gitnexus" ] || [ -f "$WORKSPACE/.gitnexus.json" ]; then
        success "Workspace indexed by GitNexus"
        ((PASS++))
    else
        info "Workspace not indexed — run: gnx-analyze"
    fi
fi

# =============================================================================
# STEP 6: Beads (Cross-Session Memory)
# =============================================================================
section "Step 7: Beads (Cross-Session Memory)"

if command -v bd >/dev/null 2>&1; then
    success "Beads CLI installed"
    ((PASS++))
else
    warning "Beads not installed — run: npm i -g beads-cli"
    ((ISSUES++))
fi

if [ -d "$WORKSPACE/.beads" ] || [ -f "$WORKSPACE/.beads.json" ]; then
    success "Beads initialized in workspace"
    ((PASS++))
else
    if [ -d "$WORKSPACE/.git" ]; then
        info "Beads not initialized — run: bd init"
    else
        info "Not a git repo — Beads requires git"
    fi
fi

# =============================================================================
# STEP 7: Agent Teams + Environment
# =============================================================================
section "Step 8: Agent Teams + Environment"

if [ "${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-}" = "1" ]; then
    success "Agent Teams enabled (CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1)"
    ((PASS++))
else
    warning "Agent Teams not enabled — add to shell: export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1"
    ((ISSUES++))
fi

# Check alias file
ALIAS_FILE="$HOME/.turboflow_aliases"
if [ -f "$ALIAS_FILE" ]; then
    success "Alias file exists: $ALIAS_FILE"
    ((PASS++))

    # Check it's sourced
    SOURCED=false
    for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
        if [ -f "$rc" ] && grep -q 'turboflow_aliases' "$rc" 2>/dev/null; then
            SOURCED=true
            break
        fi
    done
    if $SOURCED; then
        success "Aliases sourced in shell rc"
        ((PASS++))
    else
        warning "Aliases not sourced — add to .bashrc: [ -f \"$ALIAS_FILE\" ] && source \"$ALIAS_FILE\""
        ((ISSUES++))
    fi

    # Check for stale v3.x aliases
    if grep -q '# === TURBO FLOW' "$HOME/.bashrc" 2>/dev/null; then
        warning "Stale v3.x alias block found in .bashrc — should have been cleaned by setup"
        ((ISSUES++))
    fi
else
    fail "Alias file missing — run setup-turboflow-4.sh"
    ((ISSUES++))
fi

# Key aliases spot check
section "Alias Spot Check"
for alias_name in rf rf-swarm bd-ready wt-list gnx-analyze aqe-generate os; do
    if grep -q "$alias_name" "$ALIAS_FILE" 2>/dev/null; then
        success "Alias: $alias_name"
    else
        warning "Alias missing: $alias_name"
        ((ISSUES++))
    fi
done

# Key functions
for func in turbo-status turbo-help wt-add rf-spawn; do
    if grep -q "${func}" "$ALIAS_FILE" 2>/dev/null; then
        success "Function: $func"
    else
        warning "Function missing: $func"
        ((ISSUES++))
    fi
done

# =============================================================================
# STEP 8: Statusline Pro
# =============================================================================
section "Step 9: Statusline Pro"

STATUSLINE_SCRIPT="$HOME/.claude/turbo-flow-statusline.sh"
CLAUDE_SETTINGS="$HOME/.claude/settings.json"

if [ -f "$STATUSLINE_SCRIPT" ]; then
    success "Statusline script exists"
    ((PASS++))
    if [ -x "$STATUSLINE_SCRIPT" ]; then
        success "Statusline script is executable"
        ((PASS++))
    else
        warning "Statusline not executable — fixing..."
        chmod +x "$STATUSLINE_SCRIPT"
        ((ISSUES++))
    fi
else
    fail "Statusline script missing — run setup-turboflow-4.sh"
    ((ISSUES++))
fi

if [ -f "$CLAUDE_SETTINGS" ] && grep -q "turbo-flow-statusline" "$CLAUDE_SETTINGS" 2>/dev/null; then
    success "Statusline configured in settings.json"
    ((PASS++))
else
    warning "Statusline not configured in settings.json"
    ((ISSUES++))
fi

# =============================================================================
# STEP 9: CLAUDE.md + Workspace
# =============================================================================
section "Step 10: CLAUDE.md + Workspace"

if [ -f "$WORKSPACE/CLAUDE.md" ]; then
    success "CLAUDE.md exists"
    ((PASS++))

    # Check it's the v4.0 version
    if grep -q "TurboFlow 4.0" "$WORKSPACE/CLAUDE.md" 2>/dev/null; then
        success "CLAUDE.md is v4.0"
        ((PASS++))
    else
        warning "CLAUDE.md exists but may be outdated — check for 'TurboFlow 4.0' header"
        ((ISSUES++))
    fi
else
    fail "CLAUDE.md missing — run setup-turboflow-4.sh"
    ((ISSUES++))
fi

# Workspace directories
for dir in src tests docs scripts config plans; do
    if [ -d "$WORKSPACE/$dir" ]; then
        success "Directory: $dir/"
    else
        warning "Missing directory: $dir/"
        ((ISSUES++))
    fi
done

# =============================================================================
# STEP 10: Ruflo Daemon
# =============================================================================
section "Step 11: Ruflo Daemon"

if npx ruflo@latest daemon status 2>/dev/null | grep -q "running"; then
    success "Ruflo daemon running"
    ((PASS++))
else
    info "Ruflo daemon not running — start with: rf-daemon"
    # Not counted as issue — daemon is optional
fi

# =============================================================================
# STEP 11: API Keys + PATH
# =============================================================================
section "Step 12: Environment"

[ -n "${ANTHROPIC_API_KEY:-}" ] && success "ANTHROPIC_API_KEY is set" || warning "ANTHROPIC_API_KEY not set"
echo "$PATH" | grep -q "$HOME/.local/bin" && success "PATH includes ~/.local/bin" || warning "PATH missing ~/.local/bin"
echo "$PATH" | grep -q "$HOME/.claude/bin" && success "PATH includes ~/.claude/bin" || warning "PATH missing ~/.claude/bin"

# =============================================================================
# STEP 12: Fix Permissions
# =============================================================================
section "Step 13: Permissions"

CURRENT_USER=$(whoami)
sudo chown -R "$CURRENT_USER:$CURRENT_USER" "$HOME/.claude" 2>/dev/null || true
sudo chown -R "$CURRENT_USER:$CURRENT_USER" "$HOME/.local" 2>/dev/null || true
sudo chown -R "$CURRENT_USER:$CURRENT_USER" "$HOME/.config/claude" 2>/dev/null || true
sudo chown -R "$CURRENT_USER:$CURRENT_USER" /home/"$CURRENT_USER"/.vscode-server 2>/dev/null || true
sudo chown -R "$CURRENT_USER:$CURRENT_USER" /workspaces/.cache/vscode-server 2>/dev/null || true
sudo chown -R "$CURRENT_USER:$CURRENT_USER" /workspaces/.cache/npm-global 2>/dev/null || true
success "Permissions fixed"

# =============================================================================
# SUMMARY
# =============================================================================
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║      Post-Setup Verification Complete            ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo -e "  Results: ${GREEN}$PASS passed${NC}  /  ${YELLOW}$ISSUES issues${NC}"
echo ""

if [ $ISSUES -eq 0 ]; then
    echo -e "  ${GREEN}All checks passed!${NC}"
else
    echo -e "  ${YELLOW}$ISSUES issue(s) found — review warnings above.${NC}"
fi

echo ""
echo "  Next Steps:"
echo "    1. RESTART CLAUDE CODE  →  Required for MCP & plugins"
echo "    2. RELOAD SHELL         →  source ~/.bashrc"
echo "    3. SET API KEY          →  export ANTHROPIC_API_KEY=\"sk-ant-...\""
echo "    4. VERIFY               →  turbo-status"
echo ""
echo "  Quick Reference:"
echo "    ORCHESTRATION   rf-swarm, rf-spawn, rf-doctor, rf-plugins"
echo "    MEMORY          bd-ready, bd-add, ruv-remember, mem-search"
echo "    ISOLATION       wt-add, wt-remove, wt-list"
echo "    QUALITY         aqe-generate, aqe-gate, os-init"
echo "    INTELLIGENCE    hooks-train, hooks-route, neural-train"
echo "    CODEBASE        gnx-analyze, gnx-serve, gnx-wiki"
echo "    STATUS          turbo-status, turbo-help"
echo ""
