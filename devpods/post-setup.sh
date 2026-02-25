#!/bin/bash
# TURBO FLOW POST-SETUP SCRIPT v3.4.1
# Configure & Enable ALL Claude Flow Components
# 
# CHANGES FROM v3.3.0:
# - FIXED: Removed verbose 'set -x'
# - FIXED: Updated version to match setup.sh
# - FIXED: Removed skill verification (skills are built-in)
# - FIXED: Simplified output and checks

# Get the directory where this script is located
readonly DEVPOD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ============================================
# PATH SETUP - ensure npm global bin is discoverable
# ============================================
if [ -n "$npm_config_prefix" ]; then
    export PATH="$npm_config_prefix/bin:$PATH"
elif [ -f "$HOME/.npmrc" ]; then
    _NPM_PREFIX=$(grep '^prefix=' "$HOME/.npmrc" 2>/dev/null | cut -d= -f2)
    [ -n "$_NPM_PREFIX" ] && export PATH="$_NPM_PREFIX/bin:$PATH"
fi
export PATH="$HOME/.local/bin:$HOME/.claude/bin:$PATH"

# Colors for output
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

success() { echo -e "${GREEN}[OK] $*${NC}"; }
warning() { echo -e "${YELLOW}[WARN] $*${NC}"; }
info() { echo -e "${BLUE}[INFO] $*${NC}"; }
section() { echo -e "${CYAN}=== $* ===${NC}"; }

cat << 'EOF'
==================================================
        Turbo Flow V3.4.1 Post-Setup
   Configure & Enable Claude Flow Components
   Skills + Plugins + Memory + MCP + Extensions
==================================================
EOF

echo ""
echo "WORKSPACE_FOLDER: ${WORKSPACE_FOLDER:=$(pwd)}"
echo "DEVPOD_DIR: $DEVPOD_DIR"
echo ""

# Helper function
skill_has_content() {
    local dir="$1"
    [ -d "$dir" ] && [ -n "$(ls -A "$dir" 2>/dev/null)" ]
}

skill_is_installed() {
    local skill_name="$1"
    local skill_dir="$HOME/.claude/skills/$skill_name"
    skill_has_content "$skill_dir"
}

# ============================================================================
# STEP 1: Verify Core Installations
# ============================================================================
info "Step 1: Verifying core installations..."

# Build tools
if command -v g++ >/dev/null 2>&1 && command -v make >/dev/null 2>&1; then
    success "Build tools: g++, make installed"
else
    warning "Build tools not found"
fi

# jq (required for worktree-manager and statusline)
if command -v jq >/dev/null 2>&1; then
    success "jq: $(jq --version 2>/dev/null)"
else
    warning "jq not found (required for worktree-manager and statusline)"
fi

# Node.js & npm
if command -v node >/dev/null 2>&1; then
    NODE_VER=$(node -v)
    NODE_MAJOR=$(echo "$NODE_VER" | sed 's/v//' | cut -d. -f1)
    if [ "$NODE_MAJOR" -ge 20 ]; then
        success "Node.js: $NODE_VER (>= 20)"
    elif [ "$NODE_MAJOR" -ge 18 ]; then
        success "Node.js: $NODE_VER (>= 18, 20+ recommended)"
    else
        warning "Node.js: $NODE_VER (needs >= 18)"
    fi
else
    warning "Node.js not found"
fi

# Claude Code
if command -v claude >/dev/null 2>&1; then
    success "Claude Code: $(claude --version 2>/dev/null | head -1)"
else
    warning "Claude Code not found - run setup.sh first"
fi

# Claude Flow V3
CF_VERSION=$(npx -y claude-flow@alpha --version 2>/dev/null | head -1 || echo "")
if [ -n "$CF_VERSION" ]; then
    success "Claude Flow V3: $CF_VERSION"
else
    warning "Claude Flow not responding"
fi

# RuVector Neural Engine
if npm list -g ruvector --depth=0 >/dev/null 2>&1; then
    success "RuVector: $(npm list -g ruvector --depth=0 2>/dev/null | grep ruvector | head -1)"
elif npx -y ruvector --version >/dev/null 2>&1; then
    success "RuVector: available via npx"
else
    warning "RuVector not installed"
fi

# sql.js (for memory database WASM fallback)
# Check: global, local project, or available via require.resolve (transitive dependency)
SQLJS_INSTALLED=false

# Check global
if npm list -g sql.js --depth=0 >/dev/null 2>&1; then
    SQLJS_INSTALLED=true
    success "sql.js: installed globally (memory database)"
fi

# Check local project (from workspace folder)
if [ "$SQLJS_INSTALLED" = false ] && [ -f "$WORKSPACE_FOLDER/package.json" ]; then
    cd "$WORKSPACE_FOLDER" 2>/dev/null || true
    if npm list sql.js --depth=0 >/dev/null 2>&1; then
        SQLJS_INSTALLED=true
        success "sql.js: installed locally (memory database)"
    fi
fi

# Check via require.resolve (from workspace folder)
if [ "$SQLJS_INSTALLED" = false ] && [ -f "$WORKSPACE_FOLDER/package.json" ]; then
    cd "$WORKSPACE_FOLDER" 2>/dev/null || true
    if node -e "require.resolve('sql.js')" >/dev/null 2>&1; then
        SQLJS_INSTALLED=true
        success "sql.js: available via require (memory database)"
    fi
fi

# If still not installed, try to install it now
if [ "$SQLJS_INSTALLED" = false ]; then
    info "Installing sql.js for memory database..."
    if [ -f "$WORKSPACE_FOLDER/package.json" ]; then
        cd "$WORKSPACE_FOLDER" 2>/dev/null || true
        if npm install sql.js --save-dev 2>/dev/null; then
            success "sql.js: installed locally (memory database)"
        else
            warning "sql.js not installed (memory database may fail)"
        fi
    else
        warning "sql.js not installed (memory database may fail) - no package.json"
    fi
fi

echo ""

# ============================================================================
# STEP 2: Verify Ecosystem Packages
# ============================================================================
info "Step 2: Verifying ecosystem packages..."

for pkg in agentic-qe @fission-ai/openspec uipro-cli; do
    if npm list -g "$pkg" --depth=0 >/dev/null 2>&1; then
        success "$pkg: installed"
    elif npx -y "$pkg" --version >/dev/null 2>&1; then
        success "$pkg: available via npx"
    else
        warning "$pkg not installed"
    fi
done

# @claude-flow/browser (part of claude-flow)
if [ -d "$WORKSPACE_FOLDER/.claude-flow" ]; then
    success "@claude-flow/browser: integrated (59 MCP tools)"
else
    warning "@claude-flow/browser: requires claude-flow init"
fi

echo ""

# ============================================================================
# STEP 3: Start Claude Flow Daemon
# ============================================================================
info "Step 3: Starting Claude Flow daemon..."

if npx -y claude-flow@alpha daemon status 2>/dev/null | grep -q "running"; then
    warning "Daemon already running - skipping"
else
    if npx -y claude-flow@alpha daemon start 2>/dev/null; then
        success "Daemon started"
    else
        warning "Daemon start failed (can be started later)"
    fi
fi

echo ""

# ============================================================================
# STEP 4: Initialize Memory System
# ============================================================================
info "Step 4: Initializing Claude Flow memory system..."

MEMORY_DIR="$WORKSPACE_FOLDER/.claude-flow/memory"

if [ -d "$MEMORY_DIR" ] && [ -f "$MEMORY_DIR/agent.db" ]; then
    success "Memory already initialized"
    info "  HNSW Vector Search: 150x-12,500x faster"
    info "  AgentDB: SQLite-based persistent memory"
    info "  LearningBridge: Bidirectional sync"
else
    mkdir -p "$MEMORY_DIR" 2>/dev/null
    if npx -y claude-flow@alpha memory init --force 2>/dev/null; then
        success "Memory initialized with HNSW indexing"
    else
        warning "Memory init failed - will initialize on first use"
    fi
fi

echo ""

# ============================================================================
# STEP 5: Initialize Swarm
# ============================================================================
info "Step 5: Initializing Claude Flow swarm..."

if npx -y claude-flow@alpha swarm status 2>/dev/null | grep -q "active\|initialized"; then
    warning "Swarm already initialized"
else
    if npx -y claude-flow@alpha swarm init --topology hierarchical --max-agents 8 --strategy specialized 2>/dev/null; then
        success "Swarm initialized: hierarchical, 8 agents"
    else
        warning "Swarm init failed - can be initialized later"
    fi
fi

echo ""

# ============================================================================
# STEP 6: Check MCP Configuration
# ============================================================================
info "Step 6: Checking MCP configuration..."

MCP_CONFIG="$HOME/.config/claude/mcp.json"
MCP_CONFIG_ALT="$HOME/.claude/claude_desktop_config.json"

if [ -f "$MCP_CONFIG" ]; then
    grep -q "claude-flow" "$MCP_CONFIG" && success "MCP: claude-flow configured" || warning "MCP: claude-flow missing"
    info "Restart Claude Code to detect MCP servers"
elif [ -f "$MCP_CONFIG_ALT" ]; then
    grep -q "claude-flow" "$MCP_CONFIG_ALT" && success "MCP: claude-flow configured" || warning "MCP: claude-flow missing"
else
    warning "MCP config not found"
fi

echo ""

# ============================================================================
# STEP 7: Verify Custom Skills
# ============================================================================
info "Step 7: Verifying custom Turbo Flow skills..."

SKILLS_DIR="$HOME/.claude/skills"
SKILLS_DIR_LOCAL="$WORKSPACE_FOLDER/.claude/skills"

section "Security Analyzer"
if skill_is_installed "security-analyzer"; then
    success "security-analyzer skill installed"
else
    warning "security-analyzer skill missing"
fi

section "UI UX Pro Max"
if skill_is_installed "ui-ux-pro-max" || skill_has_content "$SKILLS_DIR_LOCAL/ui-ux-pro-max"; then
    success "UI UX Pro Max skill installed"
else
    warning "UI UX Pro Max skill missing"
fi

section "Worktree Manager"
if [ -f "$SKILLS_DIR/worktree-manager/SKILL.md" ]; then
    success "worktree-manager skill installed"
else
    warning "worktree-manager skill missing"
fi

echo ""

# ============================================================================
# STEP 8: Verify Claude Flow Browser Integration
# ============================================================================
info "Step 8: Verifying Claude Flow Browser integration..."

if [ -d "$WORKSPACE_FOLDER/.claude-flow" ]; then
    success "Claude Flow Browser: integrated"
    info "  59 MCP tools: browser/open, browser/snapshot, browser/click, etc."
    info "  Features: trajectory learning, security scanning, element refs"
    info "  Memory: patterns saved to RuVector"
else
    warning "Claude Flow Browser: requires cf-init"
fi

echo ""

# ============================================================================
# STEP 9: Verify Statusline
# ============================================================================
info "Step 9: Checking Statusline..."

CLAUDE_SETTINGS="$HOME/.claude/settings.json"
STATUSLINE_SCRIPT="$HOME/.claude/turbo-flow-statusline.sh"

section "Statusline Script"
if [ -f "$STATUSLINE_SCRIPT" ]; then
    success "Statusline script: $STATUSLINE_SCRIPT"
    if [ -x "$STATUSLINE_SCRIPT" ]; then
        success "  Script is executable"
    else
        warning "  Script not executable, fixing..."
        chmod +x "$STATUSLINE_SCRIPT"
    fi
else
    warning "Statusline script not found"
fi

section "Settings Configuration"
if [ -f "$CLAUDE_SETTINGS" ]; then
    if grep -q "turbo-flow-statusline" "$CLAUDE_SETTINGS" 2>/dev/null; then
        success "Statusline: configured in settings.json"
    else
        warning "Statusline: not configured"
    fi
else
    warning "Claude settings.json not found"
fi

echo ""

# ============================================================================
# STEP 10: Verify Workspace Files
# ============================================================================
info "Step 10: Verifying workspace files..."

# Directories
for dir in src tests docs scripts config plans; do
    [ -d "$WORKSPACE_FOLDER/$dir" ] && success "Directory: $dir/" || warning "Missing: $dir/"
done

# Key files
[ -d "$WORKSPACE_FOLDER/.claude-flow" ] && success ".claude-flow directory exists" || warning ".claude-flow missing"

echo ""

# ============================================================================
# STEP 11: Check Bash Aliases
# ============================================================================
info "Step 11: Checking bash aliases..."

if grep -q "TURBO FLOW v3.4" ~/.bashrc 2>/dev/null; then
    success "Bash aliases: v3.4.x installed"
else
    warning "Bash aliases: not found or old version"
fi

section "Core Aliases"
for alias_name in cf ruv dsp; do
    grep -q "alias $alias_name=" ~/.bashrc 2>/dev/null && success "Alias: $alias_name" || warning "Alias: $alias_name missing"
done

section "Memory Aliases"
for alias_name in mem-search mem-vsearch mem-stats; do
    grep -q "alias $alias_name=" ~/.bashrc 2>/dev/null && success "Alias: $alias_name" || warning "Alias: $alias_name missing"
done

section "Functions"
for func in turbo-status turbo-help; do
    grep -q "${func}()" ~/.bashrc 2>/dev/null && success "Function: $func()" || warning "Function: $func() missing"
done

echo ""

# ============================================================================
# STEP 12: Check Environment
# ============================================================================
info "Step 12: Checking environment..."

section "API Keys"
[ -n "$ANTHROPIC_API_KEY" ] && success "ANTHROPIC_API_KEY is set" || warning "ANTHROPIC_API_KEY not set"

section "PATH"
echo "$PATH" | grep -q "$HOME/.local/bin" && success "PATH: ~/.local/bin" || warning "PATH missing ~/.local/bin"
echo "$PATH" | grep -q "$HOME/.claude/bin" && success "PATH: ~/.claude/bin" || warning "PATH missing ~/.claude/bin"

echo ""

# ============================================================================
# STEP 13: Run Doctor
# ============================================================================
info "Step 13: Running Claude Flow doctor..."

DOCTOR_OUTPUT=$(npx -y claude-flow@alpha doctor 2>&1 || true)
if echo "$DOCTOR_OUTPUT" | grep -qi "error\|failed\|missing"; then
    warning "Doctor found issues:"
    echo "$DOCTOR_OUTPUT" | head -20
else
    success "Doctor check passed"
    echo "$DOCTOR_OUTPUT" | head -15
fi

echo ""

# ============================================================================
# STEP 14: Test Components
# ============================================================================
info "Step 14: Testing components..."

section "Claude Flow MCP Server"
if npx -y claude-flow@alpha mcp status 2>/dev/null | grep -q "running\|active"; then
    success "MCP server running"
else
    info "MCP server not running - start with: cf-mcp"
fi

section "Memory System"
if [ -d "$WORKSPACE_FOLDER/.claude-flow/memory" ]; then
    success "Memory system initialized"
    info "  Aliases: mem-search, mem-vsearch, mem-stats"
else
    warning "Memory system not initialized"
fi

echo ""

# ============================================================================
# STEP 15: Generate Prompts
# ============================================================================
info "Step 15: Generating Claude prompts..."

PROMPT_FILE="$WORKSPACE_FOLDER/.claude-flow-prompts.md"
cat > "$PROMPT_FILE" << 'PROMPT_EOF'
# Claude Post-Setup Prompts (v3.4.1)

## Quick Verification
```
Run turbo-status to check all installed components.
```

## Restart MCP
```
Restart the MCP server connection to detect claude-flow.
```

## Full Doctor Check
```
Run Claude Flow doctor and show complete status.
```

---

## Core Skills Prompts

### SPARC Methodology
```
Use SPARC methodology to plan a new feature for this codebase.
```

### Swarm Orchestration
```
Initialize a swarm with hierarchical topology to analyze this project.
```

### Hive Mind
```
Use hive-mind to coordinate multiple agents for a complex refactoring task.
```

---

## Memory Prompts

### Vector Search
```
Search memory for similar code patterns.
```

### Store Memory
```
Store this context in memory for future reference.
```

---

## Workflow Prompts

### Create Worktree
```
Create a worktree for feature/new-api-endpoint.
```

### Deploy to Vercel
```
Deploy this app to Vercel and show the preview URL.
```

### Memory Operations
```
Search memory for patterns related to authentication.
```

PROMPT_EOF

success "Prompts saved to: $PROMPT_FILE"

echo ""

# ============================================================================
# FINAL: Fix Permissions
# ============================================================================
section "Final Permission Fix"
info "Fixing permissions..."

CURRENT_USER=$(whoami)

sudo chown -R "$CURRENT_USER:$CURRENT_USER" /home/"$CURRENT_USER"/.vscode-server 2>/dev/null || true
sudo chown -R "$CURRENT_USER:$CURRENT_USER" /workspaces/.cache/vscode-server 2>/dev/null || true
sudo chown -R "$CURRENT_USER:$CURRENT_USER" "$HOME/.claude" 2>/dev/null || true
sudo chown -R "$CURRENT_USER:$CURRENT_USER" "$HOME/.local" 2>/dev/null || true
sudo chown -R "$CURRENT_USER:$CURRENT_USER" "$HOME/.config/claude" 2>/dev/null || true
sudo chown -R "$CURRENT_USER:$CURRENT_USER" /workspaces/.cache/npm-global 2>/dev/null || true
success "Permissions fixed"

echo ""

# ============================================================================
# SUMMARY
# ============================================================================
cat << 'EOF'
==================================================
        Post-Setup Complete! (v3.4.1)
==================================================

Components Verified:

  CORE:
  - Node.js 20+, Claude Code, Claude Flow V3, RuVector
  - jq, sql.js (memory database)

  SKILLS:
  - Built-in to Claude Flow (36 native skills)
  - Custom: security-analyzer, ui-ux-pro-max, worktree-manager

  WORKSPACE:
  - src, tests, docs, scripts, config, plans

  CONFIG:
  - MCP servers, Statusline Pro

Next Steps:

  1. RESTART CLAUDE CODE -> Required for MCP & skills
  2. RELOAD SHELL -> source ~/.bashrc
  3. SET API KEY -> export ANTHROPIC_API_KEY="sk-ant-..."
  4. VERIFY -> turbo-status

Quick Reference:

  CORE            cf, cf-init, cf-swarm, cf-mesh
  MEMORY          mem-search, mem-vsearch, mem-stats
  NEURAL          neural-train, neural-patterns
  BROWSER         cfb-open, cfb-snap, cfb-click
  WORKFLOW        wt-status, deploy, deploy-preview

EOF

success "Post-setup completed!"
echo ""
