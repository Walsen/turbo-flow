# Turbo Flow v4.0 — Workflow Guide

Validated against: Anthropic's 2026 Agentic Coding Trends Report, PACT framework for Agentic QE, DDD-for-multi-agent-systems research, Claude Code swarm best practices, and ADR community practices.

---

## What's Installed

| Layer | Components |
|-------|------------|
| **Orchestration** | Claude Code, Ruflo v3.5 (swarm, MCP, skills, browser, daemon) |
| **Memory** | Beads (cross-session, git-native JSONL), Native Tasks (session), AgentDB v3 (learned patterns, RuVector WASM) |
| **Intelligence** | Ruflo hooks intelligence, neural operations, 3-tier model routing |
| **Codebase** | GitNexus knowledge graph, blast-radius detection, MCP server |
| **Plugins** | 6 plugins: Agentic QE, Code Intelligence, Test Intelligence, Perf Optimizer, Teammate, Gastown Bridge |
| **Skills** | UI UX Pro Max (design), 36+ Ruflo auto-activated skills (SPARC, swarm, DDD, etc.) |
| **Specs** | OpenSpec (spec-driven development) |
| **Isolation** | Git worktrees per agent, PG Vector schema namespacing |
| **Monitoring** | Statusline Pro v4.0, Ruflo built-in observability |

---

## Core Philosophy

TurboFlow v4.0 follows three principles validated by research:

1. **Plan cheap, execute expensive** — Use minimal tokens to plan (Phase 1). Use swarms for parallel execution (Phase 3). Never skip planning.
2. **One bounded context per agent** — Each agent owns a single DDD bounded context with clear boundaries. Agents crossing context boundaries cause drift and merge conflicts.
3. **QE gates are phase transitions** — The Agentic QE pipeline runs after every ADR, every bounded context, every phase. Nothing moves forward until QE passes.

Additional disciplines:

- **Architecture decisions are documented and traceable** via ADRs with a 5-point Definition of Done
- **Code organization reflects business domains** via DDD bounded contexts
- **Project state persists across sessions** via Beads (issues, decisions, blockers)
- **Agents check blast radius before editing shared code** via GitNexus
- **Each parallel agent operates in isolation** via git worktrees
- **CLAUDE.md is customized per project** — generic templates produce generic work
- **Anti-Corruption Layers** protect context boundaries — agents communicate through explicit interfaces, never by reading another context's internal models

---

## Boot Sequence

Every session. No exceptions.

### Step 1 — Source Aliases

```bash
source ~/.bashrc
```

### Step 2 — Initialize Ruflo

```bash
rf-wizard
```

Use `rf-wizard` for guided setup, or `rf-init` for defaults.

### Step 3 — Verify Environment

```bash
rf-doctor
```

Fix any issues before proceeding.

### Step 4 — Check Project Memory

```bash
bd-ready
```

Loads Beads state: blockers, in-progress work, decisions from prior sessions.

### Step 5 — Index the Codebase

```bash
gnx-analyze
```

Builds the GitNexus knowledge graph for blast-radius detection.

### Step 6 — Activate Hooks Intelligence

```bash
hooks-train
```

Deep pretrain from the codebase — teaches Ruflo your project's patterns.

### Step 7 — Start the Daemon

```bash
rf-daemon
```

### Step 8 — Verify Everything

```bash
turbo-status
```

**You're now fully booted.**

### Quick Copy-Paste

```bash
source ~/.bashrc
rf-wizard
rf-doctor
bd-ready
gnx-analyze
hooks-train
rf-daemon
turbo-status
```

---

## Three-Tier Memory System

| Tier | System | What it stores | How to use |
|------|--------|---------------|------------|
| **1. Project** | Beads (`bd-*`) | Issues, decisions, blockers, roadmap items | `bd-add`, `bd-ready`, `bd-list` |
| **2. Session** | Native Tasks | Current session checklist, active work | Managed by Claude Code |
| **3. Learned** | AgentDB (`ruv-*`, `mem-*`) | Patterns, routing weights, skills | `ruv-remember`, `ruv-recall`, `mem-search` |

### Decision Tree

```
Is this about the project roadmap / blockers / dependencies / decisions?
  → Beads (bd-add)

Is this about what I'm doing right now in this session?
  → Native Tasks

Is this a learned pattern / routing weight / skill?
  → AgentDB (automatic via Ruflo)
```

### Session Protocol (MANDATORY)

**Start of session:**
1. `bd-ready` — check project state
2. Review Native Tasks from prior sessions
3. AgentDB loads automatically

**During work:**
- Project decisions → `bd add --type decision "description"`
- Discovered issues → `bd add --type issue "description"`
- Active tasks → Native Tasks

**End of session:**
- File blockers and decisions as Beads
- AgentDB persists automatically

---

## ADR + DDD Methodology

### Architecture Decision Records (ADR)

ADRs capture important architectural decisions along with their context and consequences.

**ADR Structure:**
```
docs/adr/
├── ADR-001-record-architecture-decisions.md
├── ADR-002-choose-database-technology.md
└── ...
```

**ADR Definition of Done (all 5 required):**

1. **Evidence** — data or research supporting the decision
2. **Criteria & Alternatives** — what was considered and why alternatives were rejected
3. **Agreement** — explicit status (proposed / accepted / deprecated / superseded)
4. **Documentation** — stored in `docs/adr/` and recorded in Beads
5. **Realization Plan** — how this decision maps to bounded contexts and implementation tasks

**After each ADR:** Run the Agentic QE pipeline (`aqe-generate` → `aqe-gate`) to verify the ADR is complete, consistent with other ADRs, and has no gaps.

### Domain-Driven Design (DDD)

DDD organizes code around business domains with clear bounded contexts.

**DDD Structure:**
```
src/
├── domains/
│   ├── identity/           # User management bounded context
│   │   ├── application/    # Use cases, handlers
│   │   ├── domain/         # Entities, value objects
│   │   ├── infrastructure/ # Repositories, external services
│   │   └── interfaces/     # Controllers, DTOs
│   ├── ordering/           # Order management bounded context
│   └── shared/             # Shared kernel
```

**Key DDD rules for agents:**
- Each agent owns ONE bounded context
- No agent crosses context boundaries without going through the Teammate plugin
- When contexts need to communicate, define explicit Anti-Corruption Layer interfaces
- No agent reads another context's internal models directly

---

## QE Gates (Mandatory)

The Agentic QE pipeline is the gatekeeper between every phase. Nothing moves forward until QE passes.

**When QE runs:**
- After each ADR is written
- After the full ADR/DDD plan is complete
- After CLAUDE.md customization
- After each bounded context is implemented
- After each worktree merge
- After all contexts complete (full codebase QE)
- Before every release

**What QE checks:**
- Test coverage completeness
- Security scan results
- Code quality and pattern consistency
- Missing edge cases
- Undefined integration points
- Untestable designs
- Missing acceptance criteria

**Commands:**
```bash
aqe-generate     # Generate tests and validation checks
aqe-gate         # Quality gate — GO/NO-GO decision
```

---

## Agent Isolation with Worktrees

When running parallel agents, each one gets its own worktree.

### Creating Isolated Agents

```bash
wt-add agent-1
wt-add agent-2
wt-add agent-3
```

Each `wt-add` call:
- Creates a git worktree at `.worktrees/<name>` with a timestamped branch
- Sets `DATABASE_SCHEMA` env var for PG Vector isolation
- Auto-indexes the worktree with GitNexus in the background

### Agent Roles (for swarm execution)

| Role | Responsibility | Writes code? |
|------|---------------|-------------|
| **Manager/Lead** | Plans tasks, assigns work, merges results | NO |
| **Builder** | Implements code in its own worktree | YES |
| **QA** | Runs QE pipeline, hunts edge cases, validates before merge | NO (tests only) |

### Cleanup

```bash
wt-remove agent-1
wt-remove agent-2
wt-remove agent-3
wt-clean           # Prune any stale worktrees
```

---

## Codebase Intelligence with GitNexus

Before agents edit shared code, check the blast radius.

```bash
gnx-analyze          # Index the repo (run once, or after major changes)
gnx-analyze-force    # Force re-index
gnx-serve            # Start web UI for visual exploration
gnx-wiki             # Generate a wiki from the knowledge graph
gnx-status           # Check status
```

GitNexus runs as an MCP server — Claude Code agents get knowledge graph tools natively.

---

## The Core Workflow

### Phase 1: Plan (ADR/DDD)

> Review the `/plans/research` and create a detailed ADR/DDD implementation using all the various capabilities of Ruflo self-learning, security, hooks, and other optimizations. Spawn swarm, do not implement yet.

This prompt:
- Reads your research
- Creates ADRs in `docs/adr/` (each with the 5-point Definition of Done)
- Identifies bounded contexts with aggregates, entities, value objects, domain events
- Maps each context to swarm topology, hooks strategy, security requirements
- Specifies GitNexus blast-radius checkpoints
- Defines Beads memory points and neural training points
- Creates a swarm execution plan (agent assignments, worktree allocation, merge order)
- Outputs CLAUDE.md customization spec

**QE Gate:** After each ADR and after the full plan. Do NOT proceed until QE passes.

```bash
aqe-generate
aqe-gate
bd add --type decision "ADR/DDD plan complete — QE passed"
gnx-analyze
```

### Phase 2: Customize Environment

> Update the CLAUDE.md to match the DDD we just outlined.

Replace the generic CLAUDE.md with project-specific: bounded contexts, ADR index, domain language glossary, isolation rules, agent team roles, model routing, security requirements, hooks configuration, cost guardrails.

> Update the statusline to match the DDD we just outlined using the ADRs and available hooks and helpers.

Then pretrain Ruflo on the customized environment:

```bash
hooks-train
gnx-analyze
neural-train
aqe-generate
aqe-gate
bd add --type decision "Environment customized — QE passed"
```

### Phase 3: Execute (Swarm Implement)

> Spawn swarm, implement completely, test, validate, benchmark, optimize, document, continue until complete.

This prompt:
- Creates worktrees per bounded context
- Assigns agent roles (Manager does NOT write code, Builders implement, QA validates)
- Each agent checks GitNexus blast radius before editing shared code
- Anti-Corruption Layers for cross-context communication via Teammate plugin
- Ruflo auto-routes: Opus for architecture, Sonnet for implementation, Haiku for boilerplate
- Security scans, performance profiles, documents as it goes
- Records all decisions in Beads

**QE Gate:** After each bounded context completes. After all merges. Full codebase QE before declaring done.

---

## Workflow Variations

### Continued Builds

```bash
bd-ready                    # What's the project state?
mem-search "domain-model"   # What does memory know?
gnx-status                  # Is the knowledge graph current?
```

Check blast radius before extending → create ADR if architectural change → `wt-add` → implement → QE gate → merge → `gnx-analyze` → `bd add`

### Adding Features

Before coding: `bd-ready` + blast radius + `mem-search`

If architectural change: create ADR first → QE gate on ADR → update CLAUDE.md

Then: `wt-add feature-[name]` → implement → QE gate (`aqe-generate` + `aqe-gate`) → merge → `wt-remove` → `gnx-analyze` → `bd add`

### Refactoring

1. `gnx-analyze` — current graph
2. GitNexus blast radius — what depends on this module?
3. Generate characterization tests: `aqe-generate`
4. `wt-add refactor-[name]`
5. Refactor in isolation
6. All characterization tests must still pass
7. QE gate: `aqe-generate` + `aqe-gate`
8. Merge, `wt-remove`, `gnx-analyze`
9. `bd add --type decision "Refactored [module] — QE passed"`

### Bug Fixes

1. `bd-ready` — any known issues?
2. GitNexus: trace execution path
3. `wt-add bugfix-[name]`
4. Write failing test → fix → test passes
5. QE gate: `aqe-generate` + `aqe-gate`
6. Merge, `wt-remove`, `gnx-analyze`
7. `bd add --type issue "Fixed: [description] — QE passed"`

### Production Incidents

1. `bd-ready` — recent changes?
2. GitNexus: trace affected path
3. Perf Optimizer: profile affected endpoint
4. `wt-add hotfix-[name]`
5. Minimal fix (Ruflo routes to Opus)
6. QE gate: `aqe-generate` + `aqe-gate`
7. Merge immediately
8. `bd add --type issue "INCIDENT: [root cause] — [fix] — QE passed"`
9. Follow-up ADR if needed → QE gate on ADR

### Releases

1. `bd-ready` — review all decisions/issues since last release
2. Full codebase QE: `aqe-generate` + `aqe-gate` — no release without QE pass
3. Security scan
4. Generate changelog from `bd-list`
5. `git tag -a v[X.Y.Z] -m "Release [X.Y.Z]"`
6. `bd add --type decision "Released v[X.Y.Z] — QE passed"`

---

## Tool Reference

### Swarm Topologies

| Topology | Command | When to use |
|----------|---------|-------------|
| Hierarchical | `rf-swarm` | Domain implementation (default, 8 agents max) |
| Mesh | `rf-mesh` | Refactoring, parallel work |
| Ring | `rf-ring` | Sequential pipeline tasks |
| Star | `rf-star` | Hub-and-spoke coordination |

### Memory Operations

**Beads (cross-session project memory):**

| Command | What it does |
|---------|-------------|
| `bd-ready` | Check project state (run at session start) |
| `bd-add` | Record issue/decision/blocker |
| `bd-list` | List all beads |
| `bd-status` | Beads system status |

**AgentDB / RuVector (via Ruflo):**

| Command | What it does |
|---------|-------------|
| `ruv-remember "key" "value"` | Store in AgentDB |
| `ruv-recall "query"` | Query AgentDB |
| `ruv-stats` | AgentDB statistics |
| `mem-search "query"` | Search Ruflo memory |
| `mem-store "key" "value"` | Store in Ruflo memory |
| `mem-stats` | Memory statistics |

### Intelligence Operations

| Command | What it does |
|---------|-------------|
| `hooks-train` | Deep pretrain on codebase |
| `hooks-route` | Route task to optimal agent |
| `hooks-pre` | Pre-edit hook |
| `hooks-post` | Post-edit hook |
| `neural-train` | Train neural patterns |
| `neural-status` | Neural system status |
| `neural-patterns` | View learned patterns |

### GitNexus (Codebase Intelligence)

| Command | What it does |
|---------|-------------|
| `gnx-analyze` | Index repo into knowledge graph |
| `gnx-analyze-force` | Force re-index |
| `gnx-serve` | Start web UI |
| `gnx-wiki` | Generate wiki from graph |
| `gnx-status` | Knowledge graph status |
| `gnx-mcp` | Start MCP server manually |

### Worktree Isolation

| Command | What it does |
|---------|-------------|
| `wt-add <name>` | Create worktree + branch + PG Vector schema + GitNexus index |
| `wt-remove <name>` | Remove worktree |
| `wt-list` | List active worktrees |
| `wt-clean` | Prune stale worktrees |

### Quality Engineering

| Command | What it does |
|---------|-------------|
| `aqe-generate` | Run Agentic QE pipeline — generate tests, analyze coverage, check quality |
| `aqe-gate` | Quality gate — GO/NO-GO decision |
| `rf-plugins` | List installed plugins |

### Specs

| Command | What it does |
|---------|-------------|
| `os-init` | Initialize OpenSpec in project |
| `os` | Run OpenSpec |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Commands not found | `source ~/.bashrc` |
| MCP servers not connected | `claude mcp list` — re-register with `claude mcp add ruflo -- npx -y ruflo@latest` |
| Old `cf-*` commands not working | Replaced by `rf-*` in v4.0 |
| Beads not initialized | `bd init` (requires git repo) |
| GitNexus not indexed | `gnx-analyze` from repo root |
| Ruflo not responding | `npx ruflo@latest init` then `rf-doctor` |
| Plugins not found | `rf-plugins` to check, reinstall with `npx ruflo@latest plugins install -n <name>` |
| Worktree conflicts | `wt-clean` to prune stale worktrees |
| Memory empty after restart | Beads persists in git — run `bd-ready`. AgentDB persists automatically. |
| Stale v3.x aliases in .bashrc | Setup script auto-cleans, or manually remove `# === TURBO FLOW` blocks |
| QE gate failing | Read the gap report. Fix gaps. Re-run. Don't skip. |

---

## Quick Reference

```
BOOT:       source ~/.bashrc → rf-wizard → rf-doctor → bd-ready → gnx-analyze → hooks-train → rf-daemon
PLAN:       review /plans/research → create ADR/DDD → QE gate per ADR → QE gate on full plan
CUSTOMIZE:  update CLAUDE.md → update statusline → hooks-train → gnx-analyze → QE gate
EXECUTE:    rf-swarm → agents in worktrees → QE gate per context → QE gate full codebase
FEATURE:    bd-ready → blast radius → wt-add → implement → QE gate → merge → gnx-analyze
REFACTOR:   characterization tests → wt-add → refactor → QE gate → merge → gnx-analyze
BUGFIX:     wt-add → failing test → fix → QE gate → merge → gnx-analyze
RELEASE:    full QE gate → security scan → changelog from bd-list → git tag
HANDOFF:    bd add (issues + decisions) → gnx-analyze → neural-patterns
```

---

## Component Summary

| Category | Count | Notes |
|----------|-------|-------|
| Ruflo Auto-Activated Skills | 36+ | Built-in, replace slash commands |
| Ruflo Plugins | 6 | QE, Code Intel, Test Intel, Perf, Teammate, Gastown |
| Custom Skills | 1 | UI UX Pro Max |
| Independent Tools | 2 | OpenSpec, GitNexus |
| Memory Systems | 3 | Beads, Native Tasks, AgentDB |
| **Total Components** | **23** | Complete agentic development environment |
