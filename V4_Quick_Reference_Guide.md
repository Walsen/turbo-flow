# Turbo Flow v4 + Ruflo v3.5 — Quick Reference

> Commands use TurboFlow aliases. If aliases aren't set up, use native commands shown in parentheses.

### Alias → Native Command Map

| Alias | Native Command |
|-------|---------------|
| `rf-wizard` | `npx ruflo@latest init --wizard` |
| `rf-swarm` | `npx ruflo@latest swarm init --topology hierarchical` |
| `rf-mesh` | `npx ruflo@latest swarm init --topology mesh` |
| `rf-ring` | `npx ruflo@latest swarm init --topology ring` |
| `rf-star` | `npx ruflo@latest swarm init --topology star` |
| `rf-spawn [type]` | `npx ruflo@latest agent spawn -t [type]` |
| `rf-daemon` | `npx ruflo@latest daemon start` |
| `rf-status` | `npx ruflo@latest status` |
| `rf-doctor` | `npx ruflo@latest doctor --fix` |
| `rf-init` | `npx ruflo@latest init` |
| `rf-plugins` | `npx ruflo@latest plugins list --installed` |
| `mem-store K V` | `npx ruflo@latest memory store --key "K" --value "V"` |
| `mem-search Q` | `npx ruflo@latest memory search --query "Q"` |
| `mem-stats` | `npx ruflo@latest memory stats` |
| `bd-ready` | `bd ready --json` |
| `bd-add` | `bd create "Title" -t task -p N` |
| `bd-list` | `bd list` |
| `wt-add NAME` | `git worktree add .worktrees/NAME -b NAME-$(date +%s)` |
| `wt-remove NAME` | `git worktree remove .worktrees/NAME` |
| `wt-list` | `git worktree list` |
| `wt-clean` | `git worktree prune` |
| `gnx-analyze` | `npx gitnexus analyze` |
| `gnx-serve` | `npx gitnexus serve` |
| `gnx-wiki` | `npx gitnexus wiki` |
| `aqe-generate` | `npx ruflo@latest mcp call aqe/generate-tests` |
| `aqe-gate` | `npx ruflo@latest mcp call aqe/evaluate-quality-gate` |
| `os-init` | `openspec init` |
| `hooks-train` | `npx ruflo@latest hooks pretrain` |
| `hooks-route` | `npx ruflo@latest hooks route --task "..."` |
| `neural-train` | `npx ruflo@latest neural train` |
| `neural-patterns` | `npx ruflo@latest neural patterns` |
| `turbo-status` | TF-specific statusline check |
| `turbo-help` | TF-specific help display |

---

## Boot (every session)

```bash
# Using TF aliases:
source ~/.bashrc
bd ready --json          # (native: bd ready --json)
gnx-analyze              # (native: npx gitnexus analyze)
turbo-status             # (TF-specific)

# Using native commands only:
source ~/.bashrc
bd ready --json
npx gitnexus analyze
npx ruflo@latest doctor --fix
npx ruflo@latest hooks pretrain
npx ruflo@latest daemon start
```

One-liner (aliases): `source ~/.bashrc && rf-doctor && bd ready --json && gnx-analyze && hooks-train && rf-daemon && turbo-status`

One-liner (native): `source ~/.bashrc && npx ruflo@latest doctor --fix && bd ready --json && npx gitnexus analyze && npx ruflo@latest hooks pretrain && npx ruflo@latest daemon start`

---

## The Core Loop

```
BOOT:       source ~/.bashrc → rf-doctor (npx ruflo doctor --fix) → bd ready → gnx-analyze (npx gitnexus analyze) → hooks-train (npx ruflo hooks pretrain) → turbo-status
PRD:        generate PRD → save to plans/research/PLAN.md → aqe-gate (npx @agentic-qe/v3 gate)
PLAN:       review /plans/research → create ADR/DDD → aqe-gate per ADR
CUSTOMIZE:  update CLAUDE.md → update statusline → hooks-train → gnx-analyze → aqe-gate
EXECUTE:    rf-swarm (npx ruflo swarm init) → agents in worktrees → aqe-gate per context → aqe-gate full codebase
FEATURE:    bd ready → blast radius → wt-add (git worktree add) → implement → aqe-gate → merge → gnx-analyze
REFACTOR:   characterization tests → wt-add → refactor → aqe-gate → merge → gnx-analyze
BUGFIX:     wt-add → failing test → fix → aqe-gate → merge → gnx-analyze
RELEASE:    full aqe-gate → security scan → changelog from bd list → git tag
HANDOFF:    bd create (remaining work) → bd close (done items) → gnx-analyze → neural-patterns (npx ruflo neural patterns)
```

---

## All Commands

### Ruflo Orchestration

| Alias | Native Command | What it does |
|-------|---------------|-------------|
| `rf-wizard` | `npx ruflo@latest init --wizard` | Interactive project setup |
| `rf-swarm` | `npx ruflo@latest swarm init --topology hierarchical` | Hierarchical swarm (8 agents max) |
| `rf-mesh` | `npx ruflo@latest swarm init --topology mesh` | Mesh swarm (all-to-all) |
| `rf-ring` | `npx ruflo@latest swarm init --topology ring` | Ring swarm (sequential pipeline) |
| `rf-star` | `npx ruflo@latest swarm init --topology star` | Star swarm (hub-and-spoke) |
| `rf-spawn coder` | `npx ruflo@latest agent spawn -t coder` | Spawn a typed agent |
| `rf-daemon` | `npx ruflo@latest daemon start` | Start background workers |
| `rf-status` | `npx ruflo@latest status` | Ruflo status |
| `rf-doctor` | `npx ruflo@latest doctor --fix` | Health check + auto-fix |
| `rf-init` | `npx ruflo@latest init` | Initialize Ruflo |
| `rf-plugins` | `npx ruflo@latest plugins list --installed` | List installed plugins |

### Memory

| Alias | Native Command | What it does |
|-------|---------------|-------------|
| `ruv-remember KEY VALUE` | `npx ruflo@latest memory store --key "KEY" --value "VALUE"` | Store in AgentDB |
| `ruv-recall QUERY` | `npx ruflo@latest memory search --query "QUERY"` | Query AgentDB |
| `mem-search QUERY` | `npx ruflo@latest memory search --query "QUERY"` | Search all memory tiers |
| `mem-stats` | `npx ruflo@latest memory stats` | Memory statistics |

### Beads (Task Tracker)

| Alias / Command | What it does |
|----------------|-------------|
| `bd init` | Initialize Beads in repo |
| `bd ready --json` | Show ready tasks (session start) |
| `bd create "Title" -t task -p 1` | Create a task |
| `bd create "Title" -t bug -p 0` | Create a P0 bug |
| `bd create "Title" -t epic -p 1` | Create an epic |
| `bd list` | List all issues |
| `bd list --status open` | Filter open issues |
| `bd show <id>` | Show issue details |
| `bd update <id> --claim` | Claim a task |
| `bd close <id> --reason "Done"` | Close a task |
| `bd dep add <from> <to>` | Add dependency |
| `bd dep tree <id>` | Show dependency tree |
| `bd blocked` | Show blocked issues |
| `bd daemon start` | Start auto-sync |

TF aliases: `bd-ready` → `bd ready` · `bd-add` → `bd create` · `bd-list` → `bd list`

### Worktrees

| Alias | What it does |
|-------|-------------|
| `wt-add <name>` | Create worktree + branch + PG Vector schema |
| `wt-remove <name>` | Remove worktree |
| `wt-list` | List active worktrees |
| `wt-clean` | Prune stale worktrees |

### GitNexus (Codebase Intelligence)

| Alias / Command | What it does |
|----------------|-------------|
| `gnx-analyze` | Index repo → knowledge graph |
| `gnx-serve` | Start web UI |
| `gnx-wiki` | Generate wiki from graph |
| `gitnexus status` | Index status |
| `gitnexus analyze --force` | Force full re-index |
| `gitnexus setup` | Configure MCP for editors (one-time) |
| `gitnexus mcp` | Start MCP server |

### Quality Engineering

| Alias | What it does |
|-------|-------------|
| `aqe-generate` | Generate tests + analyze coverage |
| `aqe-gate` | Quality gate — GO/NO-GO |

### OpenSpec

| Alias / Command | What it does |
|----------------|-------------|
| `os-init` | Initialize OpenSpec |
| `openspec init --tools claude` | Init for Claude Code |
| `/opsx:propose <feature>` | Create a proposal |
| `/opsx:new <name>` | Start a new change |
| `/opsx:ff` | Fast-forward all planning docs |
| `/opsx:apply` | Implement the spec |
| `/opsx:verify` | Verify implementation |
| `/opsx:archive` | Archive completed change |

### Intelligence

| Alias / Command | What it does |
|----------------|-------------|
| `hooks-train` | Deep pretrain on codebase |
| `hooks-route` | Route task to optimal agent |
| `neural-train` | Train neural patterns |
| `neural-patterns` | View learned patterns |
| `npx ruflo hooks metrics` | View intelligence metrics |
| `npx ruflo hooks build-agents` | Generate agent configs |
| `npx ruflo worker dispatch --trigger audit` | Dispatch workers |

### System

| Alias | What it does |
|-------|-------------|
| `turbo-status` | Full stack status (15 components) |
| `turbo-help` | Complete command reference |

---

## Swarm Topologies

| Topology | Command | Best for |
|----------|---------|----------|
| Hierarchical | `rf-swarm` | Feature development (default) |
| Mesh | `rf-mesh` | Parallel independent work |
| Ring | `rf-ring` | Sequential pipeline |
| Star | `rf-star` | Hub-and-spoke coordination |
| Hive-mind | `npx ruflo hive-mind init` | Advanced multi-consensus |

### Agent Types

`coordinator` · `coder` · `architect` · `tester` · `researcher` · `documenter` · `security` · `reviewer` · `optimizer` · `analyst` · `monitor`

---

## SPARC Modes

| Mode | Purpose |
|------|---------|
| `orchestrator` | Coordinate feature development |
| `coder` | Implement with TDD |
| `architect` | Design scalable systems |
| `tdd` | Test-driven development |
| `researcher` | Investigate best practices |
| `reviewer` | Code review |
| `optimizer` | Performance optimization |
| `devops` | CI/CD, infrastructure |
| `security` | Vulnerability assessment |
| `documenter` | Generate docs, ADRs |

---

## MCP Tool Invocations

> Prefix: `mcp__ruflo__` or `mcp__claude-flow__` depending on registration. Check with `claude mcp list`.

```
# Swarm
mcp__ruflo__swarm_init { topology: "hierarchical", maxAgents: 8, strategy: "adaptive" }
mcp__ruflo__agent_spawn { type: "coder", capabilities: ["typescript", "react"] }

# SPARC
mcp__ruflo__sparc_mode { mode: "tdd", task_description: "...", options: { coverage_target: 90 } }

# Memory
mcp__ruflo__memory_store { key: "...", value: "...", namespace: "patterns" }
mcp__ruflo__memory_search { query: "...", limit: 5 }

# Browser (59 tools)
mcp__ruflo__browser_open { url: "...", enableSecurity: true }
mcp__ruflo__browser_snapshot { interactive: true }
mcp__ruflo__browser_click { ref: "@e3" }
mcp__ruflo__browser_fill { ref: "@e1", value: "..." }
mcp__ruflo__browser_start_trajectory { goal: "..." }
mcp__ruflo__browser_end_trajectory { success: true, verdict: "..." }
```

---

## Copy-Paste Prompts

### New Project

```
Initialize a new project with Ruflo. Run rf-wizard, then:
1. bd init — initialize Beads task tracker
2. openspec init --tools claude — initialize OpenSpec
3. gitnexus analyze — build knowledge graph
4. wt-add main-dev — create primary worktree
Scaffold a [Next.js/Express/FastAPI] app with src/, tests/, docs/, scripts/, config/, plans/.
Use a hierarchical swarm with architect, coder, and tester agents.
```

### Generate PRD

```
I want to build [describe product]. Generate a comprehensive PRD covering:
- Problem statement, target users, success criteria
- Functional requirements (P0/P1/P2 with user stories and acceptance criteria)
- Non-functional requirements (performance, security, scalability, accessibility)
- Technical constraints and required integrations
- Out of scope items
Save to plans/research/PLAN.md. Run QE to validate completeness.
```

### Plan (ADR/DDD)

```
Review /plans/research and create a detailed ADR/DDD implementation using all Ruflo
capabilities. Spawn swarm, do NOT implement yet. Create ADRs in docs/adr/ with 5-point
Definition of Done. Identify bounded contexts, define aggregates/entities/events. Map each
context to swarm topology and worktree allocation. Run aqe-gate after each ADR.
Do NOT implement any code. Plan only.
```

### Execute

```
Spawn swarm, implement completely, test, validate, benchmark, optimize, document,
continue until complete. Follow the execution plan from /plans/. Create worktrees per
bounded context. Each agent checks GitNexus blast radius before editing shared code.
Use Teammate plugin for cross-context coordination. Run aqe-gate after each context.
Do not stop until all contexts pass quality gates.
```

### Add Feature

```
Add [feature] to the [bounded context]. Before coding:
1. bd ready --json — any related blockers?
2. GitNexus blast radius — what does this touch?
3. mem-search "[related area]" — any learned patterns?
Then: wt-add feature-[name] → implement with TDD → aqe-gate → merge → gnx-analyze
```

### Refactor

```
Refactor [module] to [goal]. Safety protocol:
1. gnx-analyze — blast radius
2. Generate characterization tests: aqe-generate
3. wt-add refactor-[name]
4. Refactor in isolation, all characterization tests must pass
5. aqe-gate → merge → gnx-analyze
```

### Bug Fix

```
Bug: [describe]. Steps:
1. bd ready --json — any known issues?
2. GitNexus: trace execution path
3. wt-add bugfix-[name]
4. Write failing test → fix → test passes
5. aqe-gate → merge → gnx-analyze
6. bd close <id> --reason "Fixed: [description]"
```

### Hotfix (Production)

```
Incident: [symptoms].
1. bd ready --json — recent changes?
2. GitNexus: trace affected path
3. wt-add hotfix-[name] (branch from production tag)
4. Minimal fix (Ruflo routes to Opus for critical reasoning)
5. aqe-gate → merge immediately
6. bd create "INCIDENT: [root cause] — [fix]" -t bug -p 0
```

### Code Review

```
Review [PR/branch] using Agent Teams. Spawn 3 reviewers:
1. Correctness: logic bugs, edge cases, error handling
2. Security: injection, auth bypass, data exposure
3. Performance: N+1 queries, memory leaks
Cross-reference with gnx-analyze blast radius and neural-patterns.
Output: categorized findings (critical/warning/info) with fix suggestions.
```

### Dependency Update

```
Update [package] from [old] to [new]:
1. gnx-analyze — blast radius
2. Code Intelligence: find deprecated API usage
3. wt-add dep-update-[package]
4. Update + fix all breaking changes
5. aqe-gate → merge → gnx-analyze
```

### Release

```
Prepare release v[X.Y.Z]:
1. bd list — review all issues since last release
2. aqe-generate + aqe-gate — full codebase QE
3. Security scan
4. Generate changelog from bd list
5. git tag -a v[X.Y.Z] -m "Release [X.Y.Z]"
```

### Security Audit

```
Run a comprehensive security audit:
- Static: dependency vulns, code patterns (injection/XSS/CSRF), secrets scan, config review
- Dynamic: browser automation to test auth flows, injection on inputs, privilege escalation
- Architecture: gnx-analyze trust boundaries, data flow review, encryption check
Output: vulnerability report with severity ratings and fix recommendations.
```

### Performance Optimization

```
Profile and optimize [module/endpoint]:
1. Perf Optimizer plugin for profiling
2. Identify top 5 bottlenecks
3. For each: gnx-analyze dependencies → propose fix → TDD implement → measure before/after
4. Record optimizations: ruv-remember "perf-[area]" "[details]"
```

### Onboard Existing Codebase

```
Onboard me on [repo]:
1. gitnexus analyze — knowledge graph
2. gitnexus wiki — generate documentation
3. hooks-train — pretrain on codebase
4. bd init && bd ready --json — task state
5. neural-train && neural-patterns — learn conventions
6. Code Intelligence: identify architecture, tech debt, test gaps
Give me: architecture summary, dependencies, hot paths, technical debt.
```

### Session Handoff

```
Ending session. Before I go:
1. bd create "Continue: [unfinished work]" -t task -p 1
2. bd close <id> --reason "Completed: [summary]" (for done items)
3. gnx-analyze — update graph
4. neural-patterns — capture what was learned
5. Summarize what a new agent needs to continue.
```

---

## Three-Tier Memory

| Tier | System | Store | Retrieve |
|------|--------|-------|----------|
| **Project** | Beads | `bd create "..." -t task -p N` | `bd ready --json` · `bd list` |
| **Session** | Native Tasks | Automatic | Automatic |
| **Learned** | AgentDB | `ruv-remember KEY VALUE` | `ruv-recall QUERY` · `mem-search QUERY` |

**Rule:** Tasks/bugs/features → Beads · Patterns/knowledge → AgentDB · Active work → Native Tasks

---

## Plugins

| Plugin | MCP Tools | Purpose |
|--------|-----------|---------|
| Agentic QE | 16 | 58 agents — TDD, coverage, security, chaos engineering |
| Code Intelligence | — | Patterns, anti-patterns, dead code, complexity |
| Test Intelligence | — | Test generation, gap analysis, flaky test detection |
| Perf Optimizer | — | Profiling, bottleneck detection |
| Teammate | 21 | Agent Teams ↔ Ruflo bridge, semantic routing |
| Gastown Bridge | 20 | WASM orchestration (352x), Beads sync, convoys |

---

## Agent Roles (Swarm)

| Role | Writes code? | Responsibility |
|------|-------------|----------------|
| Manager/Lead | NO | Plans, assigns, merges |
| Builder | YES | Implements in own worktree |
| QA | NO (tests only) | Runs QE pipeline, validates |

**Rule:** One bounded context per agent. Anti-Corruption Layer for cross-context communication.

---

## Model Routing

| Tier | Use for | Cost |
|------|---------|------|
| **Opus** | Architecture, complex refactors, security analysis | $$$ |
| **Sonnet** | Feature implementation, code review, documentation | $$ |
| **Haiku** | Test generation, linting, formatting, boilerplate | $ |

Default guardrail: **$15/hr**

---

## Statusline (15 components)

```
LINE 1: [Project] name | [Model] Sonnet | [Git] branch | [TF] 4.0 | [SID] abc123
LINE 2: [Tokens] 50k/200k | [Ctx] #######--- 65% | [Cache] 42% | [Cost] $1.23 | [Time] 5m
LINE 3: [+150] [-50] | [READY]
```

---

## Infrastructure

| Platform | Command |
|----------|---------|
| DevPod | `devpod up https://github.com/marcuspat/turbo-flow --ide vscode` |
| Codespaces | Push to GitHub → Open in Codespace → auto-runs |
| Manual | `cd turbo-flow/v4 && ./. devcontainer/setup-turboflow-4.sh` |
| macOS/Linux | See `macosx_linux_setup.md` |
| Rackspace | See `spot_rackspace_setup_guide.md` |
| Google Cloud | See `google_cloud_shell_setup.md` |

---

## v3 → v4 Migration

| v3 | v4 |
|----|-----|
| `cf-init` | `rf-init` |
| `cf-swarm` | `rf-swarm` |
| `cf-doctor` | `rf-doctor` |
| `/sparc` commands | Auto-activated skills (just describe what you want) |
| No cross-session memory | `bd ready`, `bd create` |
| No worktree isolation | `wt-add`, `wt-remove` |
| No codebase graph | `gnx-analyze` |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Commands not found | `source ~/.bashrc` |
| MCP not connected | `claude mcp list` → re-register |
| Old `cf-*` commands | Use `rf-*` instead |
| Beads not initialized | `bd init` (requires git repo) |
| GitNexus not indexed | `gitnexus analyze` from repo root |
| Ruflo not responding | `npx ruflo@latest init` → `rf-doctor` |
| QE gate failing | Read gap report → fix gaps → re-run |
| Slash commands gone | v4 auto-activates skills — just describe naturally |

---

*Quick Reference for Turbo Flow v4.0 + Ruflo v3.5 · March 2026*
