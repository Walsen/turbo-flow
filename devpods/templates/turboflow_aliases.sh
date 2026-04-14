# =============================================================================
# TurboFlow 4.0 Aliases
# =============================================================================

# --- Agent Teams ---
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

# --- Claude Code ---
alias claude-hierarchical='claude --dangerously-skip-permissions'
alias dsp='claude --dangerously-skip-permissions'

# --- Ruflo (replaces ALL cf-* aliases) ---
alias rf='npx ruflo@latest'
alias rf-init='npx ruflo@latest init'
alias rf-wizard='npx ruflo@latest init --wizard'
alias rf-doctor='npx ruflo@latest doctor --fix'
alias rf-swarm='npx ruflo@latest swarm init --topology hierarchical --max-agents 8 --strategy specialized'
alias rf-mesh='npx ruflo@latest swarm init --topology mesh'
alias rf-ring='npx ruflo@latest swarm init --topology ring'
alias rf-star='npx ruflo@latest swarm init --topology star'
alias rf-daemon='npx ruflo@latest daemon start'
alias rf-status='npx ruflo@latest status'
alias rf-migrate='npx ruflo@latest migrate run --backup'
alias rf-plugins='npx ruflo@latest plugins list'

# Spawn agents
rf-spawn() { npx ruflo@latest agent spawn -t "${1:-coder}" --name "${2:-agent-$RANDOM}"; }
rf-task() { npx ruflo@latest swarm "$1" --parallel; }

# --- RuVector / AgentDB (accessed through ruflo) ---
alias ruv='npx ruflo@latest agentdb'
alias ruv-stats='npx ruflo@latest agentdb stats'
alias ruv-init='npx ruflo@latest agentdb init'
ruv-remember() { npx ruflo@latest agentdb store --key "$1" --value "$2"; }
ruv-recall() { npx ruflo@latest agentdb query "$1"; }

# --- Memory (ruflo native) ---
alias mem-search='npx ruflo@latest memory search'
alias mem-store='npx ruflo@latest memory store'
alias mem-stats='npx ruflo@latest memory stats'

# --- Beads (cross-session memory) ---
alias bd-ready='bd ready'
alias bd-list='bd list'
alias bd-status='bd status'
bd-add() {
    local title="${1:?Usage: bd-add 'title' type [priority] ['description']}"
    local type="${2:-task}"
    local priority="${3:-1}"
    local description="${4:-}"
    if [ -n "$description" ]; then
        bd create "$title" -t "$type" -p "$priority" --description "$description"
    else
        bd create "$title" -t "$type" -p "$priority"
    fi
}

# --- Dolt (Beads storage backend) ---
alias dolt-status='dolt status 2>/dev/null || echo "Not in a Dolt repo"'
alias dolt-log='dolt log 2>/dev/null || echo "Not in a Dolt repo"'
alias bd-push='bd dolt push'
alias bd-pull='bd dolt pull'

# --- Git Worktrees (agent isolation) ---
wt-add() {
    local name="${1:?Usage: wt-add <agent-name>}"
    git worktree add ".worktrees/$name" -b "$name/$(date +%s)"
    echo "Worktree created: .worktrees/$name"
    export DATABASE_SCHEMA="wt_${name}_$(date +%s)"
    if command -v npx &>/dev/null; then
        (cd ".worktrees/$name" && npx gitnexus analyze 2>/dev/null &)
    fi
}
wt-remove() {
    local name="${1:?Usage: wt-remove <agent-name>}"
    git worktree remove ".worktrees/$name" --force 2>/dev/null
    echo "Worktree removed: $name"
}
wt-list() { git worktree list; }
wt-clean() { git worktree prune; }

# --- GitNexus (codebase knowledge graph) ---
alias gnx='npx gitnexus'
alias gnx-analyze='npx gitnexus analyze'
alias gnx-analyze-force='npx gitnexus analyze --force'
alias gnx-mcp='npx gitnexus mcp'
alias gnx-serve='npx gitnexus serve'
alias gnx-status='npx gitnexus status'
alias gnx-wiki='npx gitnexus wiki'
alias gnx-list='npx gitnexus list'
alias gnx-clean='npx gitnexus clean'

# --- Agentic QE (via ruflo plugin) ---
alias aqe='npx ruflo@latest plugins run agentic-qe'
alias aqe-generate='npx ruflo@latest plugins run agentic-qe generate'
alias aqe-gate='npx ruflo@latest plugins run agentic-qe gate'

# --- OpenSpec (spec-driven development) ---
alias os='npx @fission-ai/openspec'
alias os-init='npx @fission-ai/openspec init'

# --- Hooks Intelligence (ruflo native) ---
alias hooks-pre='npx ruflo@latest hooks pre-edit'
alias hooks-post='npx ruflo@latest hooks post-edit'
alias hooks-train='npx ruflo@latest hooks pretrain --depth deep'
alias hooks-route='npx ruflo@latest hooks route'

# --- Neural (ruflo native) ---
alias neural-train='npx ruflo@latest neural train'
alias neural-status='npx ruflo@latest neural status'
alias neural-patterns='npx ruflo@latest neural patterns'

# --- Usage monitoring ---
alias claude-usage='claude usage 2>/dev/null || echo "Run inside claude session"'

# --- TurboFlow Meta ---
turbo-status() {
    echo "╔══════════════════════════════════════════╗"
    echo "║       TurboFlow 4.0 Status Check         ║"
    echo "╚══════════════════════════════════════════╝"
    echo ""
    echo "Core:"
    claude --version 2>/dev/null && echo "  ✓ Claude Code" || echo "  ✗ Claude Code"
    npx ruflo@latest --version 2>/dev/null && echo "  ✓ Ruflo" || echo "  ✗ Ruflo"
    echo ""
    echo "Memory:"
    command -v dolt &>/dev/null \
        && echo "  ✓ Dolt $(dolt version 2>/dev/null | awk 'NR==1{print $NF}')" \
        || echo "  ✗ Dolt"
    command -v bd &>/dev/null \
        && echo "  ✓ Beads $(bd --version 2>/dev/null | head -1)" \
        || echo "  ✗ Beads"
    [ -d ".beads" ] \
        && echo "  ✓ Beads initialized" \
        || echo "  ○ Beads not initialized (run: bd init)"
    echo "  Agent Teams: ${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-off}"
    echo ""
    echo "Plugins:"
    npx ruflo@latest plugins list 2>/dev/null | head -10 || echo "  Run: rf-plugins"
    echo ""
    echo "Codebase Intelligence:"
    command -v gitnexus &>/dev/null && echo "  ✓ GitNexus" || echo "  ○ GitNexus (via npx)"
    echo ""
    echo "Workspace:"
    [ -f "CLAUDE.md" ] && echo "  ✓ CLAUDE.md" || echo "  ✗ CLAUDE.md"
    git worktree list 2>/dev/null | head -5
}

turbo-help() {
    echo "TurboFlow 4.0 — Quick Reference"
    echo ""
    echo "Orchestration:  rf-wizard | rf-swarm | rf-spawn coder | rf-doctor | rf-plugins"
    echo "Memory:         bd-ready | bd-add 'title' bug 1 'desc' | ruv-remember K V | mem-search Q"
    echo "Isolation:      wt-add agent-1 | wt-remove agent-1 | wt-list"
    echo "Quality:        aqe-generate | aqe-gate | os-init | os"
    echo "Intelligence:   hooks-train | hooks-route | neural-train | neural-patterns"
    echo "Codebase:       gnx-analyze | gnx-serve | gnx-wiki"
    echo "Status:         turbo-status | turbo-help"
}
