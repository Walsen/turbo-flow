#!/bin/bash
# =============================================================================
# TurboFlow 4.0 Post-Setup Verification Script
# =============================================================================

readonly DEVPOD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# PATH setup — source all the places things might be installed
export PATH="$HOME/.local/bin:$HOME/.claude/bin:$HOME/.npm-global/bin:$PATH"
if [ -n "$npm_config_prefix" ]; then
    export PATH="$npm_config_prefix/bin:$PATH"
elif [ -f "$HOME/.npmrc" ]; then
    _NPM_PREFIX=$(grep '^prefix=' "$HOME/.npmrc" 2>/dev/null | cut -d= -f2)
    [ -n "$_NPM_PREFIX" ] && export PATH="$_NPM_PREFIX/bin:$PATH"
fi
NPM_BIN=$(npm bin -g 2>/dev/null || echo "")
[ -n "$NPM_BIN" ] && export PATH="$NPM_BIN:$PATH"

# Source aliases/env if available
[ -f "$HOME/.turboflow_aliases" ] && source "$HOME/.turboflow_aliases" 2>/dev/null || true
[ -f "$HOME/.bashrc" ] && source "$HOME/.bashrc" 2>/dev/null || true

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

WORKSPACE="${WORKSPACE_FOLDER:-$(pwd)}"
ISSUES=0
PASS=0

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

if command -v g++ >/dev/null 2>&1 && command -v make >/dev/null 2>&1; then
    success "Build tools (g++, make)"; ((PASS++))
else
    warning "Build tools not found"; ((ISSUES++))
fi

if command -v jq >/dev/null 2>&1; then
    success "jq $(jq --version 2>/dev/null)"; ((PASS++))
else
    warning "jq not found"; ((ISSUES++))
fi

if command -v node >/dev/null 2>&1; then
    NODE_VER=$(node -v)
    NODE_MAJOR=$(echo "$NODE_VER" | sed 's/v//' | cut -d. -f1)
    if [ "$NODE_MAJOR" -ge 20 ]; then
        success "Node.js $NODE_VER"; ((PASS++))
    else
        warning "Node.js $NODE_VER (v20+ required)"; ((ISSUES++))
    fi
else
    fail "Node.js not found"; ((ISSUES++))
fi

if command -v claude >/dev/null 2>&1; then
    success "Claude Code $(claude --version 2>/dev/null | head -1)"; ((PASS++))
else
    fail "Claude Code not found"; ((ISSUES++))
fi

RF_VERSION=$(npx ruflo@latest --version 2>/dev/null | head -1 || echo "")
if [ -n "$RF_VERSION" ]; then
    success "Ruflo $RF_VERSION"; ((PASS++))
else
    fail "Ruflo not responding"; ((ISSUES++))
fi

# =============================================================================
# STEP 2: Ruflo MCP + Doctor
# =============================================================================
section "Step 2: Ruflo MCP + Health Check"

# Check all possible config locations claude might write to
MCP_OK=false
for cfg in \
    "$HOME/.claude.json" \
    "$HOME/.config/claude/mcp.json" \
    "$HOME/.claude/claude_desktop_config.json" \
    "$WORKSPACE/.mcp.json" \
    "$HOME/.claude.json"; do
    if [ -f "$cfg" ] && grep -q "ruflo" "$cfg" 2>/dev/null; then
        MCP_OK=true
        break
    fi
done
# Also check claude mcp list output directly
if ! $MCP_OK && claude mcp list 2>/dev/null | grep -q "ruflo"; then
    MCP_OK=true
fi

if $MCP_OK; then
    success "Ruflo MCP server registered"; ((PASS++))
else
    warning "Ruflo MCP not found — run: claude mcp add ruflo -- npx -y ruflo@latest"; ((ISSUES++))
fi

DOCTOR_OUTPUT=$(npx ruflo@latest doctor 2>&1 || true)
if echo "$DOCTOR_OUTPUT" | grep -qi "critical\|fatal"; then
    warning "Ruflo doctor found critical issues"; ((ISSUES++))
else
    success "Ruflo doctor passed"; ((PASS++))
fi

# =============================================================================
# STEP 3: Ruflo Plugins
# =============================================================================
section "Step 3: Ruflo Plugins (6)"

# Check multiple possible plugin locations
check_plugin() {
    local name="$1"
    local display="$2"
    for base in \
        "$WORKSPACE/.claude-flow/plugins" \
        "$HOME/.claude-flow/plugins" \
        "$HOME/.ruflo/plugins" \
        "$HOME/.npm-global/lib/node_modules/@claude-flow" \
        "$(npm root -g 2>/dev/null)/@claude-flow"; do
        local short_name="${name#@claude-flow/}"
        if [ -d "$base/$name" ] || [ -d "$base/$short_name" ]; then
            success "$display"; ((PASS++)); return
        fi
    done
    warning "$display — not found (run: npx ruflo@latest plugins install -n $name)"; ((ISSUES++))
}

check_plugin "@claude-flow/plugin-agentic-qe"        "Agentic QE (58 QE agents, TDD, coverage)"
check_plugin "@claude-flow/plugin-code-intelligence" "Code Intelligence (analysis, patterns)"
check_plugin "@claude-flow/plugin-test-intelligence" "Test Intelligence (generation, gap analysis)"
check_plugin "@claude-flow/plugin-perf-optimizer"    "Perf Optimizer (profiling, bottlenecks)"
check_plugin "@claude-flow/teammate-plugin"          "Teammate Plugin (Agent Teams bridge)"
check_plugin "@claude-flow/plugin-gastown-bridge"    "Gastown Bridge (WASM orchestration)"

# =============================================================================
# STEP 4: OpenSpec
# =============================================================================
section "Step 4: OpenSpec"

if npm list -g @fission-ai/openspec --depth=0 >/dev/null 2>&1 || \
   npx @fission-ai/openspec --version >/dev/null 2>&1; then
    success "OpenSpec available"; ((PASS++))
else
    warning "OpenSpec not installed — run: npm i -g @fission-ai/openspec"; ((ISSUES++))
fi

# =============================================================================
# STEP 5: UI UX Pro Max Skill
# =============================================================================
section "Step 5: UI UX Pro Max Skill"

if [ -n "$(ls -A "$HOME/.claude/skills/ui-ux-pro-max" 2>/dev/null)" ]; then
    success "UI UX Pro Max skill installed (global)"; ((PASS++))
elif [ -n "$(ls -A "$WORKSPACE/.claude/skills/ui-ux-pro-max" 2>/dev/null)" ]; then
    success "UI UX Pro Max skill installed (local)"; ((PASS++))
else
    warning "UI UX Pro Max skill missing — run: npx uipro-cli init --ai claude"; ((ISSUES++))
fi

# =============================================================================
# STEP 6: GitNexus
# =============================================================================
section "Step 6: GitNexus (Codebase Knowledge Graph)"

if command -v gitnexus >/dev/null 2>&1; then
    success "GitNexus installed globally"; ((PASS++))
elif npx gitnexus --version >/dev/null 2>&1; then
    success "GitNexus available via npx"; ((PASS++))
else
    warning "GitNexus not available — run: npm i -g gitnexus"; ((ISSUES++))
fi

# GitNexus MCP — check all locations
GNX_MCP=false
for cfg in \
    "$HOME/.claude.json" \
    "$HOME/.config/claude/mcp.json" \
    "$HOME/.claude/claude_desktop_config.json" \
    "$WORKSPACE/.mcp.json"; do
    if [ -f "$cfg" ] && grep -q "gitnexus" "$cfg" 2>/dev/null; then
        GNX_MCP=true; break
    fi
done
if ! $GNX_MCP && claude mcp list 2>/dev/null | grep -q "gitnexus"; then
    GNX_MCP=true
fi

if $GNX_MCP; then
    success "GitNexus MCP registered"; ((PASS++))
else
    warning "GitNexus MCP not registered — run: npx gitnexus setup"; ((ISSUES++))
fi

if [ -d "$WORKSPACE/.git" ]; then
    if [ -d "$WORKSPACE/.gitnexus" ] || [ -f "$WORKSPACE/.gitnexus.json" ]; then
        success "Workspace indexed by GitNexus"; ((PASS++))
    else
        info "Workspace not indexed — run: gnx-analyze"
    fi
fi

# =============================================================================
# STEP 7: Beads
# =============================================================================
section "Step 7: Beads (Cross-Session Memory)"

if command -v dolt >/dev/null 2>&1; then
    success "Dolt $(dolt version 2>/dev/null | head -1) installed"; ((PASS++))
else
    warning "Dolt not installed — Beads requires Dolt. Install from https://docs.dolthub.com"; ((ISSUES++))
fi

if command -v bd >/dev/null 2>&1; then
    success "Beads CLI installed"; ((PASS++))
else
    warning "Beads not installed — run: npm i -g @beads/bd"; ((ISSUES++))
fi

if [ -d "$WORKSPACE/.beads" ] || [ -f "$WORKSPACE/.beads.json" ]; then
    success "Beads initialized in workspace"; ((PASS++))
elif [ -d "$WORKSPACE/.git" ]; then
    info "Beads not initialized — run: bd init"
fi

# =============================================================================
# STEP 8: Agent Teams + Aliases
# =============================================================================
section "Step 8: Agent Teams + Environment"

# Check env var — also check /etc/environment and rc files since this runs non-interactive
AGENT_TEAMS_OK=false
if [ "${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-}" = "1" ]; then
    AGENT_TEAMS_OK=true
elif grep -q 'CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1' /etc/environment 2>/dev/null; then
    AGENT_TEAMS_OK=true
elif grep -q 'CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS' "$HOME/.bashrc" "$HOME/.zshrc" 2>/dev/null; then
    AGENT_TEAMS_OK=true
elif grep -q 'CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS' "$HOME/.turboflow_aliases" 2>/dev/null; then
    AGENT_TEAMS_OK=true
fi

if $AGENT_TEAMS_OK; then
    success "Agent Teams enabled"; ((PASS++))
else
    warning "Agent Teams not configured — add: export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1"; ((ISSUES++))
fi

ALIAS_FILE="$HOME/.turboflow_aliases"
if [ -f "$ALIAS_FILE" ]; then
    success "Alias file exists: $ALIAS_FILE"; ((PASS++))
    SOURCED=false
    for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
        grep -q 'turboflow_aliases' "$rc" 2>/dev/null && SOURCED=true && break
    done
    $SOURCED && { success "Aliases sourced in shell rc"; ((PASS++)); } \
             || { warning "Aliases not sourced in shell rc"; ((ISSUES++)); }
else
    fail "Alias file missing — run setup.sh"; ((ISSUES++))
fi

section "Alias Spot Check"
# Check pure aliases
for a in rf rf-swarm bd-ready gnx-analyze os; do
    grep -q "alias $a=" "$ALIAS_FILE" 2>/dev/null \
        && { success "Alias: $a"; } \
        || { warning "Alias missing: $a"; ((ISSUES++)); }
done
# Check functions (wt-list, aqe-generate defined as functions not aliases)
for f in turbo-status turbo-help wt-add wt-list rf-spawn aqe-generate; do
    grep -q "${f}()" "$ALIAS_FILE" 2>/dev/null \
        && { success "Function: $f"; } \
        || { warning "Function missing: $f"; ((ISSUES++)); }
done

# =============================================================================
# STEP 9: Statusline
# =============================================================================
section "Step 9: Statusline Pro"

STATUSLINE_SCRIPT="$HOME/.claude/turbo-flow-statusline.sh"
if [ -f "$STATUSLINE_SCRIPT" ]; then
    success "Statusline script exists"; ((PASS++))
    [ -x "$STATUSLINE_SCRIPT" ] \
        && { success "Statusline script is executable"; ((PASS++)); } \
        || { chmod +x "$STATUSLINE_SCRIPT"; success "Statusline script made executable"; ((PASS++)); }
else
    fail "Statusline script missing"; ((ISSUES++))
fi

if [ -f "$HOME/.claude/settings.json" ] && grep -q "turbo-flow-statusline" "$HOME/.claude/settings.json" 2>/dev/null; then
    success "Statusline configured in settings.json"; ((PASS++))
else
    warning "Statusline not in settings.json"; ((ISSUES++))
fi

# =============================================================================
# STEP 10: CLAUDE.md + Workspace dirs
# =============================================================================
section "Step 10: CLAUDE.md + Workspace"

if [ -f "$WORKSPACE/CLAUDE.md" ]; then
    success "CLAUDE.md exists"; ((PASS++))
    grep -q "TurboFlow 4.0" "$WORKSPACE/CLAUDE.md" 2>/dev/null \
        && { success "CLAUDE.md is v4.0"; ((PASS++)); } \
        || { warning "CLAUDE.md may be outdated"; ((ISSUES++)); }
else
    fail "CLAUDE.md missing"; ((ISSUES++))
fi

for dir in src tests docs scripts config plans; do
    [ -d "$WORKSPACE/$dir" ] \
        && { success "Directory: $dir/"; } \
        || { warning "Missing: $dir/"; ((ISSUES++)); }
done

# =============================================================================
# STEP 11: Daemon (info only)
# =============================================================================
section "Step 11: Ruflo Daemon"
npx ruflo@latest daemon status 2>/dev/null | grep -q "running" \
    && { success "Ruflo daemon running"; ((PASS++)); } \
    || info "Ruflo daemon not running — start with: rf-daemon"

# =============================================================================
# STEP 12: Environment
# =============================================================================
section "Step 12: Environment"

[ -n "${ANTHROPIC_API_KEY:-}" ] \
    && { success "ANTHROPIC_API_KEY is set"; ((PASS++)); } \
    || warning "ANTHROPIC_API_KEY not set"
echo "$PATH" | grep -q "$HOME/.local/bin" \
    && { success "PATH includes ~/.local/bin"; ((PASS++)); } \
    || warning "PATH missing ~/.local/bin"
echo "$PATH" | grep -q "$HOME/.claude/bin" \
    && { success "PATH includes ~/.claude/bin"; ((PASS++)); } \
    || warning "PATH missing ~/.claude/bin"

# =============================================================================
# STEP 13: Fix Permissions
# =============================================================================
section "Step 13: Permissions"
CURRENT_USER=$(whoami)
sudo chown -R "$CURRENT_USER:$CURRENT_USER" "$HOME/.claude" 2>/dev/null || true
sudo chown -R "$CURRENT_USER:$CURRENT_USER" "$HOME/.local" 2>/dev/null || true
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
[ $ISSUES -eq 0 ] \
    && echo -e "  ${GREEN}All checks passed!${NC}" \
    || echo -e "  ${YELLOW}$ISSUES issue(s) found — review warnings above.${NC}"
echo ""
echo "  Next Steps:"
echo "    1. RESTART CLAUDE CODE  →  Required for MCP & plugins"
echo "    2. RELOAD SHELL         →  source ~/.bashrc"
echo "    3. SET API KEY          →  export ANTHROPIC_API_KEY=\"sk-ant-...\""
echo "    4. VERIFY               →  turbo-status"
echo ""
echo "  Quick Reference:"
echo "    ORCHESTRATION   rf-swarm, rf-spawn, rf-doctor, rf-plugins"
echo "    MEMORY          bd-ready, bd-add, mem-store, mem-search"
echo "    ISOLATION       wt-add, wt-remove, wt-list"
echo "    QUALITY         aqe-generate, aqe-gate, os-init"
echo "    INTELLIGENCE    hooks-train, hooks-route, neural-train"
echo "    CODEBASE        gnx-analyze, gnx-serve, gnx-wiki"
echo "    STATUS          turbo-status, turbo-help"
echo ""
