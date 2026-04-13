# Turbo Flow v4 + Ruflo v3.5 — The Definitive Prompt & Workflow Guide

> **One document. Every feature. Every workflow. Every scenario.**
> Copy-paste prompts for Claude Code that leverage the full power of both platforms.
>
> **Aliases vs native commands:** This guide uses TurboFlow shell aliases (e.g. `gnx-analyze`). If aliases aren't set up, use native commands instead (e.g. `npx gitnexus analyze`). See the [full alias → native command mapping table](#all-aliases--native-commands) at the end, or refer to the inline annotations in each section.

---

## How This Works

The core loop is 4 phases:

1. **PRD** — Generate a Product Requirements Document from your idea or research. Save to `plans/research/PLAN.md`. This is the input that drives everything.
2. **Plan** — ADR/DDD from the PRD, using Ruflo's self-learning, hooks, security, and optimizations. Swarm plans but does NOT implement.
3. **Customize** — Update CLAUDE.md and statusline to match the DDD you just outlined. This is how agents know your project.
4. **Execute** — Swarm implements completely: code, test, validate, benchmark, optimize, document. Continue until done.

**After every phase and every ADR completion**, the Agentic QE plugin runs the complete QE agent pipeline (`aqe-generate` → `aqe-gate`) to verify the output before proceeding. No phase is considered complete until QE passes.

### Key Principles (from research)

- **Plan cheap, execute expensive** — Phase 1 uses minimal tokens to plan. Phase 3 uses swarms for parallel execution. This matches Anthropic's recommended pattern.
- **One bounded context per agent** — DDD research confirms: each agent should own a single bounded context with clear boundaries. Agents crossing context boundaries cause drift and merge conflicts.
- **Worktree isolation is mandatory** — Every serious multi-agent framework converges on git worktrees. No shared working directory between parallel agents. Ever.
- **QE gates are phase transitions, not just end-of-line checks** — The PACT framework recommends quality gates at every phase boundary, not just before release.
- **CLAUDE.md is your operating system** — It's not documentation. It's the instruction set every agent reads before doing anything. A generic CLAUDE.md produces generic work. A project-specific CLAUDE.md produces project-aligned work.
- **Beads + ADRs = institutional memory** — Decisions recorded in Beads survive sessions. ADRs survive team changes. Together they prevent the "why did we do this?" problem that kills projects at month 3.

---

## What's Installed

| Layer | Components |
|-------|------------|
| **Interface** | Claude Code CLI, Open WebUI (4 instances), Statusline Pro v4.0 |
| **Orchestration** | Ruflo v3.5 — 60+ agents, 215+ MCP tools, auto-activated skills, AgentDB v3, RuVector WASM, SONA, 3-tier model routing, 59 browser MCP tools, observability, gating |
| **Memory** | Beads (cross-session Dolt-powered issue/task tracker), Native Tasks (session), AgentDB v3 (learned patterns, RuVector WASM, HNSW 150x–12,500x acceleration) |
| **Intelligence** | Ruflo hooks (27 hooks + 12 background workers), neural operations, 3-tier model routing |
| **Codebase** | GitNexus knowledge graph, blast-radius detection, MCP server |
| **Plugins** | 6 plugins: Agentic QE (58 agents, 16 MCP tools), Code Intelligence, Test Intelligence, Perf Optimizer, Teammate (21 MCP tools), Gastown Bridge (20 MCP tools) |
| **Skills** | UI UX Pro Max (design), 36+ Ruflo auto-activated skills (SPARC, swarm, DDD, etc.) |
| **Specs** | OpenSpec (spec-driven development) |
| **Isolation** | Git worktrees per agent, PG Vector schema namespacing |
| **Infrastructure** | DevPod, GitHub Codespaces, Rackspace Spot Instances, Google Cloud Shell |

---

## Table of Contents

1. [Setup & Installation](#1-setup--installation)
2. [Session Boot Sequence](#2-session-boot-sequence)
3. [Three-Tier Memory System](#3-three-tier-memory-system)
4. [Phase 0.5 — Generate the PRD](#4-phase-05--generate-the-prd)
5. [Phase 1 — Plan (ADR/DDD)](#5-phase-1--plan-adrddd)
6. [Phase 2 — Customize the Environment](#6-phase-2--customize-the-environment)
7. [Phase 3 — Execute (Swarm Implement)](#7-phase-3--execute-swarm-implement)
8. [Swarm Orchestration Deep Dive](#8-swarm-orchestration-deep-dive)
9. [SPARC Methodology](#9-sparc-methodology)
10. [Git Worktrees & Agent Isolation](#10-git-worktrees--agent-isolation)
11. [Beads — Cross-Session Memory](#11-beads--cross-session-memory)
12. [GitNexus — Codebase Intelligence](#12-gitnexus--codebase-intelligence)
13. [AgentDB & Vector Memory](#13-agentdb--vector-memory)
14. [Agent Teams (Experimental)](#14-agent-teams-experimental)
15. [Plugins Deep Dive](#15-plugins-deep-dive)
16. [Browser Automation (59 MCP Tools)](#16-browser-automation-59-mcp-tools)
17. [Intelligence & Learning System](#17-intelligence--learning-system)
18. [Feature Development](#18-feature-development)
19. [Refactoring](#19-refactoring)
20. [Testing & Quality Engineering](#20-testing--quality-engineering)
21. [Code Review & PR Workflows](#21-code-review--pr-workflows)
22. [Performance Optimization](#22-performance-optimization)
23. [Security Auditing](#23-security-auditing)
24. [DevOps & Deployment](#24-devops--deployment)
25. [UI/UX Design (Pro Max Skill)](#25-uiux-design-pro-max-skill)
26. [OpenSpec — Spec-Driven Development](#26-openspec--spec-driven-development)
27. [Model Routing & Cost Control](#27-model-routing--cost-control)
28. [Statusline & Monitoring](#28-statusline--monitoring)
29. [Infrastructure (DevPod / Codespaces / Rackspace)](#29-infrastructure)
30. [Maintenance & Diagnostics](#30-maintenance--diagnostics)
31. [Compound Workflows — Real-World Scenarios](#31-compound-workflows--real-world-scenarios)
32. [CLAUDE.md Customization Template](#32-claudemd-customization-template)
33. [Troubleshooting](#33-troubleshooting)
34. [Quick Reference](#34-quick-reference)

---

## 1. Setup & Installation

### First-time install (DevPod — recommended)

```bash
# macOS
brew install loft-sh/devpod/devpod
devpod up https://github.com/marcuspat/turbo-flow --ide vscode

# Linux
curl -L -o devpod "https://github.com/loft-sh/devpod/releases/latest/download/devpod-linux-amd64"
sudo install devpod /usr/local/bin
devpod up https://github.com/marcuspat/turbo-flow --ide vscode

# Windows
choco install devpod
devpod up https://github.com/marcuspat/turbo-flow --ide vscode
```

### GitHub Codespaces

```
Push to GitHub → Open in Codespace → .devcontainer runs automatically.
The devpods/setup.sh script installs the complete stack.
```

### Manual install

```bash
git clone https://github.com/marcuspat/turbo-flow -b main
cd turbo-flow
chmod +x devpods/setup.sh
./devpods/setup.sh
source ~/.bashrc
turbo-status
```

### Initialize Ruflo in any project

```bash
npx ruflo@latest init --wizard      # Interactive guided setup
npx ruflo@latest init --force       # Non-interactive, overwrite existing
```

### Register Ruflo as MCP server in Claude Code

```bash
claude mcp add ruflo -- npx -y ruflo@latest mcp start
```

### First time on a new project

```bash
# Using TF aliases:
rf-init               # Initialize Ruflo
gnx-analyze           # Build codebase knowledge graph
bd init               # Initialize Beads task tracker
hooks-train           # Pretrain Ruflo on this codebase

# Using native commands:
npx ruflo@latest init
npx gitnexus analyze
bd init
npx ruflo@latest hooks pretrain
```

### Post-setup verification (13 checks)

```bash
./post-devpods/setup.sh    # Runs 13 automated checks on the full stack
```

### Generate CLAUDE.md from project context

```bash
./scripts/generate-claude-md.sh   # Auto-generates CLAUDE.md with:
                                   # - 3-tier memory protocol (Beads → Native Tasks → AgentDB)
                                   # - Isolation rules (one worktree per agent)
                                   # - Agent Teams rules (max 3 teammates, recursion depth 2)
                                   # - Model routing tiers (Opus/Sonnet/Haiku)
                                   # - Plugin reference
                                   # - Cost guardrails ($15/hr)
```

### UI UX Pro Max skill (design)

```bash
# Installed as part of Step 4 of devpods/setup.sh
# uipro-cli provides: component patterns, accessibility, responsive layouts, design tokens
# Auto-activated when describing UI/UX work — no manual invocation needed
```

---

## 2. Session Boot Sequence

**Every session. No exceptions.**

```bash
# Using TF aliases:
source ~/.bashrc
bd-ready              # → bd ready --json (load project state)
gnx-analyze           # → npx gitnexus analyze (refresh knowledge graph)
turbo-status          # TF-specific (full stack health check, 15 components)

# Using native commands:
source ~/.bashrc
bd ready --json
npx gitnexus analyze
npx ruflo@latest doctor --fix
npx ruflo@latest hooks pretrain
npx ruflo@latest daemon start
```

### Quick copy-paste boot

```bash
# Using TF aliases:
source ~/.bashrc && rf-wizard && rf-doctor && bd ready --json && gnx-analyze && hooks-train && rf-daemon && turbo-status

# Using native commands:
source ~/.bashrc && npx ruflo@latest init --wizard && npx ruflo@latest doctor --fix && bd ready --json && npx gitnexus analyze && npx ruflo@latest hooks pretrain && npx ruflo@latest daemon start
```

If anything fails, run `rf-doctor` (native: `npx ruflo@latest doctor --fix`) to auto-diagnose and fix.

---

## 3. Three-Tier Memory System

| Tier | System | What it stores | Alias → Native Command |
|------|--------|---------------|------------------------|
| **1. Project** | Beads (`bd`) | Tasks, bugs, features, epics, dependencies, blockers | `bd-ready` → `bd ready --json` · `bd-add` → `bd create "..." -t task -p N` · `bd-list` → `bd list` · `bd close`, `bd show`, `bd dep` (native only) |
| **2. Session** | Native Tasks | Current session checklist, active work | Managed by Claude Code automatically |
| **3. Learned** | AgentDB | Patterns, routing weights, vector embeddings | `mem-store K V` → `npx ruflo memory store --key "K" --value "V"` · `mem-search Q` → `npx ruflo memory search --query "Q"` · `mem-stats` → `npx ruflo memory stats` |

### Decision Tree

```
Is this a work item — task, bug, feature, epic, or blocker?
  → Beads (bd create "..." -t task/bug/feature/epic -p N)

Is this about what I'm doing right now in this session?
  → Native Tasks

Is this a learned pattern / routing weight / reusable knowledge?
  → AgentDB (automatic via Ruflo, or manual via mem-store)
```

### Session Protocol (mandatory)

**Start:** `bd ready --json` → Review Native Tasks → AgentDB loads automatically

**During:** New work items → `bd create "..." -t task -p N` | Claim work → `bd update <id> --claim` | Active tasks → Native Tasks

**End:** Close finished work → `bd close <id> --reason "..."` | Create tasks for remaining work → `bd ready --json` to verify state

---

## 4. Phase 0.5 — Generate the PRD

Before any planning happens, you need a Product Requirements Document. This is the input that drives everything.

### 4.1 — PRD from a Business Idea

> I want to build [describe the product/feature/system]. Generate a comprehensive Product Requirements Document (PRD) covering:
>
> **Product Overview:**
> - Problem statement — what pain does this solve?
> - Target users — who is this for?
> - Success criteria — how do we know it works?
>
> **Functional Requirements:**
> - Core features (P0 — must have)
> - Secondary features (P1 — should have)
> - Nice-to-have features (P2 — could have)
> - For each feature: user story, acceptance criteria, edge cases
>
> **Non-Functional Requirements:**
> - Performance targets (response times, throughput)
> - Security requirements (auth, data protection, compliance)
> - Scalability requirements (users, data volume, growth)
> - Accessibility requirements (WCAG level)
> - Infrastructure constraints (where this runs, budget)
>
> **Technical Constraints:**
> - Required integrations (APIs, services, databases)
> - Technology preferences or mandates
> - Deployment target (DevPod, Codespaces, Rackspace, etc.)
>
> **Out of Scope:**
> - What this project explicitly does NOT do (prevents scope creep)
>
> Save the PRD to `plans/research/PLAN.md`
>
> After saving, run QE to validate the PRD has no gaps: acceptance criteria for every feature, no undefined terms, no conflicting requirements, testable success criteria.

After the PRD is generated:

```bash
mkdir -p plans/research
aqe-generate           # Validate PRD completeness
aqe-gate               # QE gate — PRD must pass before planning
bd create "PRD complete — plans/research/PLAN.md — QE passed" -t task -p 2
gnx-analyze            # Index the new docs
```

### 4.2 — PRD from Existing Research

> Review all files in `/plans/research/` and synthesize them into a single comprehensive PRD. Resolve any conflicts between sources. Identify gaps where requirements are undefined or ambiguous. Save the consolidated PRD to `plans/research/PLAN.md`.
>
> Run QE to validate completeness — every feature needs acceptance criteria, every requirement needs to be testable.

### 4.3 — PRD for an Existing Codebase

> Analyze the current codebase using GitNexus (`gnx-analyze`). Review the existing architecture, bounded contexts, and ADRs. Then generate a PRD for [new feature/system] that integrates with what already exists.
>
> The PRD must reference: existing bounded contexts it touches, existing ADRs it depends on or extends, blast-radius analysis for the changes, and migration path if existing behavior changes.
>
> Save to `plans/research/PLAN.md`. Run QE to validate.

---

## 5. Phase 1 — Plan (ADR/DDD)

### 5.1 — Research-Driven ADR/DDD Planning

This is the core planning prompt. It reads your PRD, creates the full architecture plan, and uses every Ruflo intelligence feature — but does NOT implement.

> Review the `/plans/research` and create a detailed ADR/DDD implementation using all the various capabilities of Ruflo self-learning, security, hooks, and other optimizations. Spawn swarm, do not implement yet.
>
> Specifically:
>
> **ADR Requirements:**
> - Create ADRs in `docs/adr/` for every architectural decision
> - Each ADR must reference which Ruflo capabilities it leverages (hooks, security scanning, model routing, AgentDB patterns, etc.)
> - Include cost/complexity estimates per bounded context using the 3-tier model routing (Opus/Sonnet/Haiku)
>
> **ADR Definition of Done (all 5 required):**
> 1. **Evidence** — data or research supporting the decision
> 2. **Criteria & Alternatives** — what was considered and why alternatives were rejected
> 3. **Agreement** — explicit status (proposed/accepted/deprecated/superseded)
> 4. **Documentation** — stored in `docs/adr/` and recorded in Beads
> 5. **Realization Plan** — how this decision maps to bounded contexts and implementation tasks
>
> **DDD Requirements:**
> - Identify all bounded contexts from the research
> - Define aggregates, entities, value objects, domain events per context
> - Map context boundaries and integration points
> - Specify which contexts can be parallelized via worktrees
>
> **Ruflo Integration:**
> - Map each bounded context to swarm topology (hierarchical, mesh, ring, star)
> - Define hooks strategy: which pre/post hooks apply to each context
> - Define security scanning requirements per context
> - Specify GitNexus blast-radius checkpoints (where agents must check before editing)
> - Define Beads memory points (what decisions/issues to persist)
> - Define neural training points (what patterns should Ruflo learn from this project)
>
> **Output:**
> - ADR files in `docs/adr/`
> - DDD domain map
> - Swarm execution plan (agent assignments, worktree allocation, merge order)
> - CLAUDE.md customization spec (what needs to change for this project)
> - Updated `/plans/` with the full implementation plan
>
> **QE Gate (mandatory):**
> - After each ADR is written, run `aqe-generate` + `aqe-gate`
> - After the full DDD plan, run QE across all ADRs and domain map
> - Do NOT proceed to implementation until QE passes with no critical gaps
>
> Do NOT implement any code. Plan only.

After this runs:

```bash
aqe-generate
aqe-gate
bd create "ADR/DDD plan complete — [N] bounded contexts, [N] ADRs — QE passed" -t task -p 2
gnx-analyze
```

### 5.2 — Variations

**API-heavy project — add:**

> Also create an API specification covering all endpoints identified in the bounded contexts. Define request/response schemas, auth requirements, rate limits, and error contracts.

**UI-heavy project — add:**

> Also define the component architecture using UI UX Pro Max patterns. Map each bounded context to its UI surface: pages, components, design tokens, accessibility requirements.

**Data-heavy project — add:**

> Also define the data architecture: schemas, migrations, indexes, replication strategy, backup policy. Map each bounded context to its data store and specify cross-context query patterns.

---

## 6. Phase 2 — Customize the Environment

### 6.1 — Customize CLAUDE.md

> Update the CLAUDE.md to match the DDD we just outlined. Replace the generic template with project-specific context:
>
> - **Identity**: What this project is, its business purpose, target users
> - **Bounded Contexts**: List all contexts from our DDD, their responsibilities, and boundaries
> - **ADR Index**: Reference all ADRs by number with one-line summaries
> - **Domain Language**: Ubiquitous language glossary — terms agents must use correctly
> - **Memory Protocol**: Keep the 3-tier protocol but add project-specific Beads categories
> - **Isolation Rules**: Keep the worktree rules but specify which contexts get their own worktrees
> - **Agent Teams Rules**: Specify which agent roles this project needs
> - **Model Routing**: Specify which parts need Opus vs Sonnet vs Haiku
> - **GitNexus Checkpoints**: List the shared code paths where agents MUST check blast radius before editing
> - **Security Requirements**: Project-specific security rules from the ADRs
> - **Hooks Configuration**: Which pre/post hooks are active and what they enforce
> - **Cost Guardrails**: Adjust the $15/hr cap if needed for this project
> - **Stack Reference**: Update with project-specific tools, frameworks, and conventions

### 6.2 — Customize Statusline

> Update the statusline to match the DDD we just outlined using the ADRs and available hooks and helpers. The statusline should reflect: current bounded context, swarm status, memory tier usage, active hooks, cost tracking, and active worktrees.

### 6.3 — Pretrain Ruflo on the Plan

```bash
# Using TF aliases:
hooks-train            # Deep pretrain with the new CLAUDE.md and ADRs
gnx-analyze            # Rebuild graph with ADR/DDD docs included
neural-train           # Train neural patterns on the project structure
aqe-generate && aqe-gate   # QE gate — environment must be consistent

# Using native commands:
npx ruflo@latest hooks pretrain
npx gitnexus analyze
npx ruflo@latest neural train
npx ruflo@latest mcp call aqe/generate-tests && npx ruflo@latest mcp call aqe/evaluate-quality-gate

bd create "Environment customized for [project name] — QE passed" -t task -p 2
```

---

## 7. Phase 3 — Execute (Swarm Implement)

### 7.1 — Full Implementation

> Spawn swarm, implement completely, test, validate, benchmark, optimize, document, continue until complete.
>
> Follow the execution plan from `/plans/`:
> - Create worktrees per bounded context as specified in the plan
> - Each agent checks GitNexus blast radius before editing shared code
> - Use the Teammate plugin for cross-context coordination
> - Use the Gastown Bridge for WASM-accelerated orchestration
> - Ruflo auto-routes: Opus for architecture, Sonnet for implementation, Haiku for boilerplate
> - Security scan each context as it completes
> - Performance profile critical paths with Perf Optimizer
> - Document everything in the codebase (not separate docs)
> - Record all decisions in Beads as you go
>
> **Agent Roles (each agent owns ONE bounded context):**
> - Manager/Lead: plans tasks, assigns work, merges results — does NOT write production code
> - Builder: implements code changes in its own worktree
> - QA: runs QE pipeline, hunts edge cases, validates each context before merge
>
> **Anti-Corruption Layer**: When contexts need to communicate, define explicit interfaces. No agent reads another agent's internal models directly.
>
> **QE Gate**: After each bounded context completes. After all merges. Full codebase QE before declaring done.
>
> Do not stop until all contexts are implemented, tested, QE-verified, and passing quality gates.

### 7.2 — Incremental (One Context at a Time)

> Implement the [context name] bounded context only. Follow the ADR/DDD plan.
>
> 1. `wt-add [context-name]`
> 2. Implement all domain logic, services, interfaces
> 3. Use UI UX Pro Max for any UI components in this context
> 4. Security scan
> 5. Performance profile
> 6. `aqe-generate` + `aqe-gate` — fix any gaps before proceeding
> 7. Document
> 8. Merge to main
> 9. `wt-remove [context-name]`
> 10. `gnx-analyze`
> 11. `bd create "[context-name] implemented and merged — QE passed" -t task -p 2`
>
> Do NOT move to the next context until QE passes on this one.

### 7.3 — Parallel Implementation

> Implement these contexts in parallel using the swarm execution plan:
>
> ```
> wt-add [context-a]
> wt-add [context-b]
> wt-add [context-c]
> ```
>
> `rf-swarm`
>
> Each agent works in isolation. Teammate plugin coordinates shared interfaces.
> Each agent runs `aqe-generate` + `aqe-gate` on its context before marking complete.
>
> When all complete:
> 1. Merge in the order specified in the plan
> 2. `aqe-gate` after each merge
> 3. `gnx-analyze` after each merge
> 4. Final full QE pipeline across entire codebase
> 5. `wt-clean`
> 6. `bd create "Parallel implementation complete — QE passed all contexts" -t task -p 2`

---

## 8. Swarm Orchestration Deep Dive

### Available Topologies

| Topology | Command | When to use |
|----------|---------|-------------|
| Hierarchical | `rf-swarm` | Domain implementation (default, 8 agents max) |
| Mesh | `rf-mesh` | Refactoring, parallel independent work |
| Ring | `rf-ring` | Sequential pipeline tasks |
| Star | `rf-star` | Hub-and-spoke coordination |

### Prompt: Hierarchical Feature Swarm

```
Use rf-swarm to coordinate a hierarchical swarm for building [feature].
Spawn these agents:
- coordinator: planning, delegation, monitoring
- architect: system design, API contracts
- coder: implementation (TypeScript/React)
- tester: TDD, unit tests, integration tests
- reviewer: code review, security checks

Max 8 agents. Use 3-tier model routing (Opus for architect, Sonnet for coder, Haiku for tester).
Each agent gets its own worktree via wt-add.
Store all decisions in Beads via bd-add.
```

### Prompt: Mesh Swarm for Parallel Tasks

```
Initialize a mesh swarm with rf-mesh for parallel execution:
- Agent 1: Migrate auth module from REST to GraphQL
- Agent 2: Update all test suites for the new API
- Agent 3: Update documentation and OpenAPI specs
- Agent 4: Run security scan on the new endpoints

All agents share memory via AgentDB. Coordinate via consensus.
Report blast radius using gnx-analyze before merging.
```

### Prompt: Ring Swarm for Pipeline Processing

```
Set up a ring swarm (rf-ring) as a processing pipeline:
Stage 1 (researcher): Analyze requirements and prior art
Stage 2 (architect): Design the solution architecture
Stage 3 (coder): Implement the solution
Stage 4 (tester): Write and run all tests
Stage 5 (reviewer): Final review and quality gate

Each stage passes its output to the next. Store intermediate results in Beads.
```

### MCP Tool Direct Invocations

> **Note on MCP tool names:** The prefix depends on how you registered the MCP server. If you ran `claude mcp add ruflo ...` the prefix is `mcp__ruflo__`. If you registered as `claude-flow`, use `mcp__claude-flow__`. The tool names after the prefix are the same either way. Check with `claude mcp list` to verify your registration.

```
mcp__ruflo__swarm_init { topology: "hierarchical", config: { maxAgents: 12 } }
mcp__ruflo__agent_spawn { type: "coordinator", capabilities: ["planning", "delegation"] }
mcp__ruflo__agent_spawn { type: "coder", capabilities: ["typescript", "react", "testing"] }
mcp__ruflo__agent_spawn { type: "architect", capabilities: ["system-design", "api-contracts"] }
mcp__ruflo__agent_spawn { type: "researcher", capabilities: ["documentation-analysis"] }
mcp__ruflo__agent_spawn { type: "documenter", capabilities: ["technical-writing", "markdown"] }
mcp__ruflo__agent_spawn { type: "security", capabilities: ["vulnerability-assessment", "pentest"] }
```

---

## 9. SPARC Methodology

> **S**pecification → **P**seudocode → **A**rchitecture → **R**efinement → **C**ompletion

SPARC modes auto-activate in Ruflo v3.5. Just describe what you want naturally.

### Prompt: Full SPARC Pipeline

```
Build [feature description] using the full SPARC pipeline:

1. SPECIFICATION: Define requirements, acceptance criteria, edge cases
2. PSEUDOCODE: Write algorithmic pseudocode before real code
3. ARCHITECTURE: Design the system — modules, interfaces, data flow
4. REFINEMENT: Implement with TDD, iterate until all tests pass
5. COMPLETION: Final review, documentation, deployment prep

Use a hierarchical swarm with specialized agents for each phase.
Store the spec in OpenSpec format. Record all decisions in Beads.
Run gnx-analyze after completion to update the knowledge graph.
```

### Prompt: SPARC TDD Mode

```
Implement [feature] using SPARC TDD methodology:
- Write failing tests FIRST (red)
- Implement minimum code to pass (green)
- Refactor for quality (refactor)
- Target 90%+ coverage
- Use jest/pytest/[framework]

Spawn a TDD swarm: specification agent, test-writer agent, coder agent, reviewer agent.
```

### Available SPARC Modes

| Mode | Purpose |
|------|---------|
| `orchestrator` | Coordinate feature development |
| `coder` | Implement with TDD and parallel edits |
| `architect` | Design scalable systems with memory-based coordination |
| `tdd` | Test-driven development with coverage targets |
| `researcher` | Investigate best practices and prior art |
| `reviewer` | Code review with security and performance checks |
| `optimizer` | Performance optimization |
| `devops` | Deployment, CI/CD, infrastructure |
| `security` | Vulnerability assessment and hardening |
| `documenter` | Generate docs, ADRs, runbooks |

### MCP SPARC Invocations

> SPARC modes are auto-activated Claude Code skills. Just describe what you want (e.g. "implement with TDD") and the appropriate SPARC skill activates. For explicit invocation, use the `/sparc` skill prefix or the Skill tool in Claude Code.

```
# SPARC is invoked as a skill, not an MCP tool. Example prompts:
# "Implement this feature using the SPARC TDD methodology"
# "Run SPARC architecture analysis on this codebase"
# Use /sparc:tdd, /sparc:architect, /sparc:reviewer, etc. for explicit invocation
```

---

## 10. Git Worktrees & Agent Isolation

When running parallel agents, each one gets its own worktree. Each `wt-add` call creates a git worktree with a timestamped branch, sets `DATABASE_SCHEMA` env var for PG Vector isolation, and auto-indexes with GitNexus in the background.

### Commands

```bash
wt-add agent-1       # Create isolated worktree for agent
wt-add feature-auth  # Named worktree for a feature
wt-remove agent-1    # Clean up when done
wt-list              # Show all active worktrees
wt-clean             # Prune stale/orphaned worktrees
```

### How Beads Works with Worktrees

Beads uses a redirect mechanism so all worktrees share the same `.beads/` database. When you `bd init` in a worktree, it creates a redirect file pointing to the main repo's `.beads/` directory — so all agents see the same issues regardless of which worktree they're in.

```bash
# All worktrees share the same Beads database automatically:
cd ~/project/main      && bd list   # Same issues
cd ~/project/feature-1 && bd list   # Same issues
cd ~/project/feature-2 && bd list   # Same issues

# For multi-agent concurrent writes, use Dolt server mode:
bd dolt set mode server
bd dolt start

# Agents claim tasks atomically to prevent conflicts:
bd update bd-a1b2 --claim --assignee agent-coder-1

# For fully separate Beads databases (advanced):
export BEADS_DIR=~/project-beads/.beads
```

### Agent Roles (for swarm execution)

| Role | Responsibility | Writes code? |
|------|---------------|-------------|
| **Manager/Lead** | Plans tasks, assigns work, merges results | NO |
| **Builder** | Implements code in its own worktree | YES |
| **QA** | Runs QE pipeline, hunts edge cases, validates before merge | NO (tests only) |

### Prompt: Isolated Parallel Development

```
Create isolated worktrees for parallel feature development:
1. wt-add feat-auth — authentication module
2. wt-add feat-payments — payment processing
3. wt-add feat-notifications — notification system

Assign one coder agent per worktree. Each gets its own PG Vector schema namespace.
All agents share the same Beads database (auto-redirect).
Each agent claims its tasks with: bd update <id> --claim

After all three are complete:
- Run gnx-analyze on each to check blast radius
- Review conflicts before merging
- wt-clean to remove all worktrees
```

### Prompt: Worktree for Hotfix

```
Create a worktree for an emergency hotfix:
1. wt-add hotfix-[issue-number]
2. Branch from the production tag
3. Fix the issue with minimal changes
4. Run aqe-gate for quality checks
5. Create PR, get review, merge
6. wt-remove hotfix-[issue-number]

Record the fix in Beads: bd create "Hotfix: [description]" -t bug -p 0
```

### Prompt: Multi-Agent Worktree Setup with Shared Beads

```
Set up a multi-agent development environment:
1. Ensure Beads is initialized: bd init
2. Start Dolt server for concurrent access: bd dolt set mode server && bd dolt start
3. Create worktrees for each agent:
   wt-add agent-architect
   wt-add agent-coder-1
   wt-add agent-coder-2
   wt-add agent-tester

4. Each agent claims work atomically:
   bd update <task-id> --claim --assignee agent-coder-1
   bd update <task-id> --status in_progress

5. Agents track their progress:
   bd update <task-id> --comment "Implemented auth module, tests passing"

6. When done:
   bd close <task-id> --reason "Completed: [summary]"
   
7. Cleanup:
   bd dolt stop
   wt-clean
```

---

## 11. Beads — Cross-Session Task & Issue Tracking

> Dolt-powered version-controlled SQL database for agent task tracking. Hash-based IDs (`bd-a1b2`) prevent merge collisions. Dependency-aware with auto-ready detection. Persists across sessions via git.
>
> **Important:** Beads is an issue/task tracker, not a general-purpose memory store. Use it for tracking work items, bugs, features, blockers, and decisions — not for storing arbitrary key-value data (use AgentDB for that).

### Native CLI Commands (actual `bd` binary)

```bash
bd init                          # Initialize Beads in current repo (Dolt backend)
bd init --backend dolt           # Explicit Dolt backend
bd ready                         # Show tasks with no open blockers (run at session start)
bd ready --json                  # JSON output for agent consumption
bd create "Title" -p 1 -t task   # Create a task (types: task, bug, feature, epic)
bd create "Title" -t epic -p 0   # Create an epic
bd list                          # List all issues
bd list --status open            # Filter by status
bd list --priority 0             # Only P0 (critical)
bd show <id>                     # Show full issue details
bd update <id> --claim           # Claim a task
bd update <id> --status in_progress  # Update status
bd close <id> --reason "Done"    # Close a task
bd dep add <from> <to>           # Add dependency (from is blocked by to)
bd dep tree <id>                 # Show dependency tree
bd blocked                       # Show blocked issues
bd search "query"                # Search issues
bd daemon start                  # Start auto-sync daemon
bd daemon stop                   # Stop daemon
```

### TurboFlow Aliases (shell wrappers from devpods/setup.sh)

```bash
bd-ready             # → bd ready (check project state)
bd-add               # → bd create (create an issue/task)
bd-list              # → bd list (list all beads)
```

### Prompt: Session Startup Ritual

```
Starting a new session on [project].
1. Run bd ready --json to load all task state and see what's ready
2. Run mem-search to find relevant prior patterns
3. Run gnx-analyze to refresh the codebase graph
4. Show me: ready tasks, blocked issues, open epics

Then let's continue where we left off.
```

### Prompt: Record Architectural Decision as Issue

```
Create a decision record in Beads:
bd create "ADR: Use event sourcing for order processing" -t task -p 1

Then update its description with:
- Context: [why we're making this choice]
- Alternatives considered: [what we rejected and why]
- Consequences: [trade-offs and implications]

Tag it appropriately. This tracks the decision alongside the implementation work.
```

### Prompt: Cross-Session Handoff

```
I'm ending this session. Before I go:
1. Create issues for remaining work:
   bd create "Continue [task description]" -p 1 -t task
   bd create "Investigate [open question]" -p 2 -t task
2. Close completed tasks:
   bd close <id> --reason "Completed: [summary]"
3. Run bd daemon start for background sync
4. Summarize what a new agent would need to know to continue
```

---

## 12. GitNexus — Codebase Intelligence

> Knowledge graph of your codebase: dependencies, call chains, execution flows, blast-radius detection. Powered by KuzuDB (embedded graph database) with Tree-sitter AST parsing. Runs as an MCP server — Claude Code agents get knowledge graph tools natively.

### Native CLI Commands (actual `gitnexus` binary)

```bash
gitnexus analyze             # Index repo into knowledge graph (+ installs skills, hooks, CLAUDE.md)
gitnexus analyze --force     # Force full re-index
gitnexus setup               # Configure MCP for your editors (one-time)
gitnexus serve               # Start local HTTP server for web UI
gitnexus wiki                # Generate wiki documentation from the graph
gitnexus wiki --model <m>    # Wiki with custom LLM model
gitnexus status              # Show index status for current repo
gitnexus mcp                 # Start MCP server (stdio)
gitnexus list                # List all indexed repositories
gitnexus clean               # Delete index for current repo
```

### TurboFlow Aliases (shell wrappers)

```bash
gnx-analyze          # → gitnexus analyze
gnx-serve            # → gitnexus serve
gnx-wiki             # → gitnexus wiki
```

> **Note:** `gnx-status` and `gnx-analyze-force` appear in the TurboFlow Workflow Guide but may not be defined by the setup script. Use the native `gitnexus status` and `gitnexus analyze --force` to be safe.

### Prompt: Blast-Radius Analysis Before Refactor

```
Before refactoring [module/file/function]:
1. Run gnx-analyze to ensure the knowledge graph is current
2. Query the blast radius: what files, functions, and tests are affected?
3. List all downstream consumers of this code
4. List all upstream dependencies
5. Identify critical paths that must not break
6. Generate a risk assessment

Output a refactoring plan that addresses all affected areas.
```

### Prompt: Generate Repo Documentation

```
Use GitNexus to auto-generate comprehensive documentation:
1. Run gnx-analyze to index the entire codebase
2. Run gnx-wiki to generate a repo wiki
3. Include: module dependency graph, call chain diagrams, API surface area
4. Identify undocumented public APIs
5. Flag circular dependencies and architectural smells

Output as markdown files in docs/.
```

### Prompt: Understand Unfamiliar Code

```
I need to understand [module/file/directory]:
1. Run gnx-analyze to build the graph
2. Show me: what this code does, who calls it, what it depends on
3. Trace the execution flow from [entry point] to [endpoint]
4. Identify the key abstractions and patterns used
5. Flag any complexity hotspots or anti-patterns
```

---

## 13. AgentDB & Vector Memory

> HNSW-indexed vector search with 150x–12,500x acceleration. 8 controllers including HierarchicalMemory, SemanticRouter, MutationGuard (cryptographic proof-verified writes), and more.

### Commands

```bash
# Confirmed TF aliases (from TF README)
mem-store KEY VALUE       # Store key-value in AgentDB
mem-search QUERY          # Search Ruflo memory (all tiers)
mem-stats                 # Memory statistics

# Native Ruflo CLI (use if aliases not defined)
npx ruflo memory store --key "name" --value "data" --namespace patterns
npx ruflo memory search --query "authentication" --limit 5
```

### Prompt: Store and Recall Patterns

```
Store these development patterns in AgentDB for future reference:
- Pattern: "auth-jwt" → "JWT with refresh tokens, httpOnly cookies, 15min access / 7d refresh"
- Pattern: "api-error" → "RFC 7807 problem details, error codes enum, i18n messages"
- Pattern: "db-migration" → "Knex migrations, seed data, rollback scripts, zero-downtime"

Use mem-store for each. Tag by domain (auth, api, db).
Later I'll use mem-search to retrieve them.
```

### Prompt: Semantic Code Search

```
Search the codebase using vector memory:
1. "Find functions similar to our authentication middleware"
2. "What patterns do we use for error handling?"
3. "Show me all API endpoint definitions that handle payments"

Use mem-search with semantic matching. Return ranked results with similarity scores.
```

### MCP Invocations

```
mcp__ruflo__memory_store { key: "pattern-name", value: "pattern details", namespace: "patterns" }
mcp__ruflo__memory_search { query: "authentication best practices", limit: 5 }
mcp__ruflo__memory_query { query: "configuration", namespace: "semantic" }
```

---

## 14. Agent Teams (Experimental)

> Anthropic's native multi-agent spawning. Max 3 teammates, recursion depth 2.

### Enable

```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

### Prompt: Spawn a Review Team

```
Using Agent Teams, spawn a 3-agent review team:
1. Security reviewer: check for vulnerabilities, injection risks, auth issues
2. Performance reviewer: check for N+1 queries, memory leaks, slow paths
3. Architecture reviewer: check for coupling, SOLID violations, naming

Each agent reviews independently, then the coordinator merges findings.
Use the Teammate Plugin (21 MCP tools) to bridge with Ruflo swarms.
```

### Prompt: Pair Programming with Agent Teammate

```
Let's pair program on [feature]. Spawn a teammate agent:
- I'll be the driver (writing code)
- Teammate is the navigator (reviewing in real-time, suggesting improvements)
- Teammate watches for: bugs, test gaps, naming issues, architectural drift

Use the pair-programming skill. Teammate stores observations in Beads.
```

---

## 15. Plugins Deep Dive

### Agentic QE (Quality Engineering) — 58 agents, 16 MCP tools

```
Run the full Agentic QE pipeline:
1. aqe-generate — auto-generate tests for [module]
2. aqe-gate — run quality gate (coverage, linting, security, type-check)
3. Run chaos engineering: inject failures and verify resilience
4. Generate a quality report with coverage metrics
```

### Code Intelligence

```
Analyze the codebase with Code Intelligence plugin:
- Detect code patterns and anti-patterns
- Suggest refactoring opportunities
- Identify dead code and unused exports
- Map code complexity hotspots
- Recommend architecture improvements
```

### Test Intelligence

```
Use Test Intelligence to improve our test suite:
- Generate missing tests for uncovered code paths
- Identify flaky tests and suggest fixes
- Run gap analysis: which features lack tests?
- Prioritize test creation by risk and impact
```

### Perf Optimizer

```
Run performance profiling with Perf Optimizer:
- Profile [module/endpoint/page]
- Identify bottlenecks and hot paths
- Measure memory allocation patterns
- Suggest optimizations with estimated impact
- Compare before/after metrics
```

### Teammate Plugin — 21 MCP tools

```
Bridge Agent Teams with Ruflo swarms using Teammate Plugin:
- Semantic routing: route tasks to the best agent
- Rate limiting and circuit breaker for agent stability
- BMSSP WASM acceleration for fast coordination
```

### Gastown Bridge — 20 MCP tools

```
Use Gastown Bridge for WASM-accelerated orchestration:
- Convoy management for large agent groups
- Beads sync across distributed agents
- Graph analysis for task dependencies
- Formula parsing (352x faster via WASM)
```

---

## 16. Browser Automation (59 MCP Tools)

> Full Playwright-based browser automation with element refs (93% less context than CSS selectors), security scanning, and trajectory learning.

### Prompt: Scrape and Analyze

```
Use the browser automation tools to:
1. Open [URL] with security scanning enabled
2. Take a snapshot of the page with interactive element refs
3. Extract: navigation structure, key features, pricing info
4. Fill in any required forms using element refs (@e1, @e2, etc.)
5. Record the trajectory for learning

Store findings in AgentDB for future reference.
```

### Prompt: E2E Test with Browser Agents

```
Create end-to-end browser tests for our [feature]:
1. Start a browser session with security and memory enabled
2. Navigate through the user flow: [login → dashboard → action → verify]
3. Use element refs for all interactions
4. Record the trajectory for regression learning
5. Generate a test script from the recorded trajectory

Store the trajectory in memory for future replay.
```

### Key MCP Browser Tools

```
mcp__ruflo__browser_open { url: "https://...", enableSecurity: true }
mcp__ruflo__browser_snapshot { interactive: true }
mcp__ruflo__browser_click { ref: "@e3" }
mcp__ruflo__browser_fill { ref: "@e1", value: "user@example.com" }
mcp__ruflo__browser_type { ref: "@e2", text: "password" }
mcp__ruflo__browser_navigate { url: "https://..." }
mcp__ruflo__browser_execute_js { script: "document.title" }
# Browser automation is fully supported via the 59 browser MCP tools above
# (open, snapshot, click, fill, type, select, scroll, navigate, etc.)
```

---

## 17. Intelligence & Learning System

> 27 hooks + 12 background workers. SONA learning loop: RETRIEVE → JUDGE → DISTILL → CONSOLIDATE.

### Commands

```bash
# Confirmed TF aliases (from TF README)
hooks-train          # Deep pretrain on codebase
hooks-route          # Route task to optimal agent
neural-train         # Train neural patterns
neural-patterns      # View learned patterns

# Native Ruflo CLI (use if aliases not defined)
npx ruflo hooks pretrain
npx ruflo hooks route --task "implement OAuth2 login flow"
npx ruflo hooks metrics
npx ruflo hooks build-agents
```

### Prompt: Train and Route Optimally

```
Prepare the intelligence system for [project]:
1. hooks-train — deep pretrain on the entire codebase
2. neural-train — learn patterns, conventions, and idioms
3. neural-patterns — show me what was learned

Now route these tasks to the optimal agents:
- hooks-route "implement OAuth2 login flow"
- hooks-route "optimize database connection pooling"
- hooks-route "write comprehensive API documentation"
- hooks-route "fix flaky integration test in payments module"

For each, explain why that agent type was chosen.
```

### Prompt: Learning Loop After Task Completion

```
Task [task-id] is complete. Run the learning loop:
1. hooks post-task — record success/failure and store results
2. Let the SONA system process: RETRIEVE → JUDGE → DISTILL → CONSOLIDATE
3. Update AgentDB with new patterns learned
4. Train neural system on the new data
5. Store lessons learned in Beads

This improves future routing and agent performance.
```

---

## 18. Feature Development

### Prompt: Full Feature Build (Most Comprehensive)

```
Build [feature name] end-to-end using all available tools:

SETUP:
- wt-add feat-[name] for isolated worktree
- bd-ready to load cross-session context
- gnx-analyze to understand current codebase

PLAN:
- OpenSpec: os-init then define the spec
- SPARC: specification → pseudocode → architecture
- Store plan in Beads

BUILD:
- rf-swarm with architect + 2 coders + tester
- TDD: write tests first, implement to pass
- Each agent in its own worktree

VALIDATE:
- aqe-gate for quality
- gnx-analyze for blast radius
- Security scan
- Performance profiling

SHIP:
- Code review (Agent Teams)
- bd-add to record decisions
- Update documentation
- wt-clean to remove worktrees
```

### Prompt: Add a Feature to Existing Context

> Add [feature] to the [bounded context].
>
> Before coding:
> 1. `bd-ready` — any related blockers or decisions?
> 2. GitNexus blast radius — what does this feature touch?
> 3. `mem-search "[related area]"` — any learned patterns?
>
> If this is an architectural change, create an ADR first and update CLAUDE.md.
>
> Then:
> 1. `wt-add feature-[name]`
> 2. Implement with SPARC TDD
> 3. `aqe-generate` + `aqe-gate` — fix any gaps before merge
> 4. Merge, `wt-remove`, `gnx-analyze`
> 5. `bd create "Feature [name] shipped — QE passed" -t task -p 2`

### Prompt: Add API Endpoint

```
Add a new [GET/POST/PUT/DELETE] endpoint for [resource]:
1. Check existing patterns: mem-search "API endpoint patterns"
2. Run gnx-analyze to see current API structure
3. Use SPARC TDD:
   - Spec: define request/response schema, auth requirements, validation
   - Tests first: write integration and unit tests
   - Implement: controller, service, repository layers
   - Review: security, error handling, rate limiting
4. Update OpenAPI spec
5. Record the pattern in AgentDB: mem-store "api-[resource]" "[pattern details]"
```

### Prompt: Add Database Migration

```
Create a database migration for [change description]:
1. mem-search "database migration patterns" for existing conventions
2. Generate migration file with up/down functions
3. Generate seed data if needed
4. Test: migrate up, run tests, migrate down, verify clean state
5. Check blast radius with gnx-analyze (what queries/models are affected?)
6. Update the data model documentation
7. Record in Beads: bd-add migration decision
```

---

## 19. Refactoring

### Prompt: Large-Scale Refactor with Blast Radius

```
Refactor [module/pattern/architecture]:

ANALYSIS:
1. gnx-analyze — build/refresh knowledge graph
2. Query blast radius: every file and function affected
3. hooks-train — ensure agents understand the codebase
4. neural-patterns — review learned patterns

PLAN:
1. Define target state in OpenSpec
2. Create worktrees: wt-add refactor-phase-1, wt-add refactor-phase-2
3. Plan migration path: what order to change things

EXECUTE:
1. Generate characterization tests first: aqe-generate
2. rf-swarm with 4 coder agents (one per subsystem)
3. Each agent works in its own worktree
4. TDD: update tests first, then refactor code to pass
5. Verify no regressions after each phase

VALIDATE:
1. All characterization tests must still pass
2. aqe-gate — full quality check
3. gnx-analyze — verify blast radius is contained
4. Performance comparison: before vs after
5. bd-add — record the refactoring decisions and rationale
```

### Prompt: Extract Module / Microservice

```
Extract [component] into a standalone [module/microservice]:
1. gnx-analyze — map all dependencies and consumers
2. Identify the seam: where to cut
3. Define the interface/API contract in OpenSpec
4. Create worktree: wt-add extract-[name]
5. Move code, update imports, create Anti-Corruption Layer
6. TDD: verify all existing tests still pass
7. Add integration tests for the new boundary
8. aqe-gate — quality check
9. gnx-analyze — blast radius
10. Record decision in Beads
```

### Prompt: Rename/Restructure with Safety

```
Rename [old] to [new] across the entire codebase:
1. gnx-analyze — find every reference
2. Use Code Intelligence plugin for pattern detection
3. Plan: list every file and line that needs to change
4. Create worktree: wt-add rename-[thing]
5. Execute rename with automated find-and-replace
6. Run full test suite
7. aqe-gate for quality verification
8. gnx-analyze to confirm clean blast radius
```

---

## 20. Testing & Quality Engineering

### Prompt: Generate Comprehensive Test Suite

```
Generate a complete test suite for [module/feature]:
1. aqe-generate — auto-generate tests using Agentic QE (58 agents)
2. Include: unit tests, integration tests, edge cases, error paths
3. Use Test Intelligence to find gaps
4. Target: 90%+ line coverage, 85%+ branch coverage
5. Mark flaky tests and add retry logic
6. Generate test data factories/fixtures
7. Store coverage report in Beads
```

### Prompt: Strict TDD

```
Implement [feature] strictly with TDD:

RED: Write failing tests that define the behavior — happy path, edge cases, error cases. Tests should be readable as documentation.

GREEN: Write minimum code to make tests pass. No premature optimization. No code without a corresponding test.

REFACTOR: Clean up implementation. Extract patterns, reduce duplication. Run aqe-gate to verify quality.

Use SPARC TDD mode. Store the test patterns in AgentDB for reuse.
```

### Prompt: Chaos Engineering

```
Run chaos engineering tests on [system/service]:
1. Use Agentic QE chaos agents
2. Inject: network failures, timeout spikes, memory pressure, disk full
3. Verify: circuit breakers trip, fallbacks activate, data integrity maintained
4. Measure: recovery time, error rates, degraded performance
5. Generate chaos test report
6. Record findings in Beads
```

---

## 21. Code Review & PR Workflows

### Prompt: AI-Powered Code Review

```
Review [PR/branch/files] using Agent Teams:
Spawn 3 reviewer agents:
1. Correctness: logic bugs, edge cases, error handling
2. Security: injection, auth bypass, data exposure, dependencies
3. Performance: N+1 queries, memory leaks, unnecessary computation

Cross-reference with:
- gnx-analyze blast radius
- neural-patterns for convention violations
- mem-search for related past decisions

Output: categorized findings (critical/warning/info) with fix suggestions.
```

### Prompt: Pre-Merge Checklist

```
Run pre-merge validation for [branch]:
1. aqe-gate — full quality gate
2. gnx-analyze — blast radius report
3. Test suite: all tests pass, no regressions
4. Coverage: meets minimum thresholds
5. Security scan: no new vulnerabilities
6. Performance: no degradation on critical paths
7. Documentation: API docs updated, CHANGELOG entry added
8. Beads: all related decisions recorded

Generate a merge-readiness report.
```

---

## 22. Performance Optimization

### Prompt: Profile and Optimize

```
Profile and optimize [module/endpoint/page]:
1. Use Perf Optimizer plugin for initial profiling
2. Identify top 5 bottlenecks
3. For each bottleneck:
   - gnx-analyze: what depends on this code?
   - Propose optimization with expected impact
   - Implement with TDD (test before and after)
   - Measure: latency, throughput, memory, CPU
4. Compare before/after metrics
5. Record optimizations in AgentDB: mem-store "perf-[area]" "[details]"
```

### Prompt: Database Query Optimization

```
Optimize database queries in [module]:
1. Profile all queries: find slow ones (>100ms)
2. Analyze query plans (EXPLAIN ANALYZE)
3. Check for: N+1 queries, missing indexes, full table scans, unnecessary joins
4. Suggest indexes, query rewrites, or caching strategies
5. Test with realistic data volumes
6. Measure improvement: before/after latency
7. Record patterns in AgentDB
```

---

## 23. Security Auditing

### Prompt: Full Security Audit

```
Run a comprehensive security audit on the project:

STATIC ANALYSIS:
- Dependency vulnerabilities (npm audit, Snyk)
- Code patterns: injection, XSS, CSRF, auth bypass
- Secrets in code: API keys, passwords, tokens
- Configuration: headers, CORS, CSP, rate limiting

DYNAMIC TESTING:
- Use browser automation to test auth flows
- Attempt injection on all input fields
- Test authorization boundaries (horizontal/vertical privilege escalation)
- Check error messages for information leakage

ARCHITECTURE:
- gnx-analyze: identify trust boundaries
- Review data flow for sensitive information
- Check encryption at rest and in transit
- Review logging: no PII in logs

Output: vulnerability report with severity ratings and fix recommendations.
Store in Beads for tracking remediation.
```

---

## 24. DevOps & Deployment

### Prompt: CI/CD Pipeline Setup

```
Create a CI/CD pipeline for [project]:
1. Build stage: compile, lint, type-check
2. Test stage: unit, integration, e2e (parallel)
3. Security stage: dependency scan, SAST, secrets check
4. Quality gate: aqe-gate thresholds
5. Deploy stage: staging → smoke tests → production
6. Monitoring: health checks, alerting

Target platform: [GitHub Actions / GitLab CI / etc.]
Use SPARC DevOps mode for infrastructure design.
Store pipeline decisions in Beads.
```

### Prompt: Infrastructure as Code

```
Design and implement infrastructure for [project]:
1. Use SPARC architect mode for system design
2. Define: compute, networking, storage, security groups
3. Implement with [Terraform / Pulumi / CDK]
4. Include: auto-scaling, load balancing, monitoring
5. Create runbooks for common operations
6. Test with staging deployment
7. Record all infra decisions in Beads
```

### Prompt: Release

```
Prepare release v[X.Y.Z]:
1. bd-ready — review all decisions/issues since last release
2. Full codebase QE: aqe-generate + aqe-gate — no release without QE pass
3. Security scan
4. Generate changelog from bd-list
5. git tag -a v[X.Y.Z] -m "Release [X.Y.Z]"
6. bd create "Released v[X.Y.Z] — QE passed" -t task -p 2
```

---

## 25. UI/UX Design (Pro Max Skill)

### Prompt: Design System Creation

```
Create a design system for [project] using UI UX Pro Max:
- Design tokens: colors, typography, spacing, shadows, borders
- Component library: buttons, inputs, cards, modals, tables, navigation
- Responsive breakpoints and grid system
- Accessibility: ARIA patterns, keyboard navigation, focus management
- Dark/light theme support
- Document everything with usage examples
```

### Prompt: Component Design

```
Design and implement a [component name] using UI UX Pro Max:
- Follow our design system tokens
- Mobile-first responsive design
- WCAG 2.1 AA accessibility compliance
- Keyboard navigable
- Support both light and dark themes
- Include Storybook stories
- Write visual regression tests
```

---

## 26. OpenSpec — Spec-Driven Development

> Lightweight spec layer for AI coding assistants. Agree on what to build before code gets written. Supports 20+ AI tools including Claude Code, Cursor, Codex, and more.

### Native CLI Commands (actual `openspec` binary)

```bash
openspec init                        # Interactive initialization
openspec init --tools claude,cursor  # Non-interactive for specific tools
openspec init --tools all            # Configure all supported tools
openspec update                      # Regenerate AI tool configs after upgrade
openspec list                        # List active changes
openspec show <change-id>            # View change details
openspec validate <change-id>        # Validate spec formatting
openspec view                        # Interactive dashboard
openspec config profile              # Select workflow profile (core vs expanded)
openspec schema init <name>          # Create custom artifact schema
```

### Slash Commands (used inside Claude Code / Cursor)

```
/opsx:propose <what-to-build>        # Create a proposal (core profile)
/opsx:new <change-name>              # Start a new change (expanded profile)
/opsx:ff                             # Fast-forward: generate all planning docs
/opsx:continue                       # Continue working on current change
/opsx:apply                          # Implement the spec
/opsx:verify                         # Verify implementation matches spec
/opsx:archive                        # Archive completed change, merge specs
/opsx:onboard                        # Onboard to existing project
```

### TurboFlow Aliases (shell wrappers)

```bash
os-init              # → openspec init
os                   # → openspec (run OpenSpec)
```

### Prompt: Define a Feature Spec

```
Use OpenSpec to define the specification for [feature]:
1. os-init to initialize
2. Define:
   - User stories with acceptance criteria
   - API contracts (request/response schemas)
   - Data models and relationships
   - Business rules and validation logic
   - Error scenarios and edge cases
   - Performance requirements (SLAs)
   - Security requirements

Store the spec. Use it to drive TDD implementation with SPARC.
```

---

## 27. Model Routing & Cost Control

> 3-tier routing: Opus (complex), Sonnet (standard), Haiku (simple). Saves up to 75% on API costs.

### Prompt: Configure Cost-Optimized Routing

```
Configure model routing for cost optimization:
- Opus: architecture decisions, complex refactors, security analysis, critical reasoning
- Sonnet: feature implementation, code review, documentation
- Haiku: test generation, linting, simple queries, formatting, boilerplate

Set cost guardrail at $15/hour.
Use hooks-route to auto-select the optimal tier for each task.
Show me the cost breakdown by model tier.
```

---

## 28. Statusline & Monitoring

> 3-line real-time status display with 15 components.

```
LINE 1: [Project] name | [Model] Sonnet | [Git] branch | [TF] 4.0 | [SID] abc123
LINE 2: [Tokens] 50k/200k | [Ctx] #######--- 65% | [Cache] 42% | [Cost] $1.23 | [Time] 5m
LINE 3: [+150] [-50] | [READY]
```

### Prompt: Monitor and Optimize Resources

```
Show me the current statusline and explain:
- How much context window is used?
- What's the current cost?
- Which model tier is active?
- What's the cache hit rate?
- How many tokens have been consumed?

If context is above 70%, suggest what to compact or offload to Beads.
If cost is above $10, suggest model tier adjustments.
```

---

## 29. Infrastructure

### DevPod (recommended)

```bash
devpod up https://github.com/marcuspat/turbo-flow --ide vscode   # Launch with VS Code
devpod list                                            # List active workspaces
devpod stop [workspace]                                # Stop workspace
devpod delete [workspace]                              # Delete workspace
```

> DevPod provider setup details: see `devpod_provider_setup_guide.md` in the repo.

### GitHub Codespaces

Push to GitHub → Open in Codespace → `.devcontainer/devcontainer.json` triggers `devpods/setup.sh` automatically. See `github_codespaces_setup.md` for details.

### Rackspace Spot Instances

See `spot_rackspace_setup_guide.md` and `Rackspace_Kubernetes_Cluster_Survival_Guide.md` — Kubernetes cluster setup with auto-scaling, cost-optimized for long-running agent workloads. Spanish guide: `GUIA_COMPLETA_DEVPOD_RACKSPACE.md` and `GUIA_SUPERVIVENCIA_RACKSPACE_KUBERNETES.md`.

### macOS / Linux Native

See `macosx_linux_setup.md` — direct installation without containers.

### Google Cloud Shell

See `google_cloud_shell_setup.md` — free tier suitable for evaluation, persistent home directory.

### Migrating from v3.x

See `docs/migration-v3-to-v4.md` for the full migration guide. Quick reference:

| v3.4.1 | v4.0.0 |
|--------|--------|
| `cf-init` | `rf-init` |
| `cf-swarm` | `rf-swarm` |
| `cf-doctor` | `rf-doctor` |
| `cf-mcp` | Automatic via `rf-wizard` |
| `mem-search` | `mem-search` (unchanged) |
| `cfb-open` | Via Ruflo's bundled browser MCP tools |
| No cross-session memory | `bd ready`, `bd create` |
| No isolation | `wt-add`, `wt-remove` |
| No codebase graph | `gnx-analyze` (gitnexus) |

---

## 30. Maintenance & Diagnostics

### Prompt: Full Diagnostic

```
Run a complete diagnostic on the Turbo Flow environment:
1. turbo-status — check all 15 statusline components
2. rf-doctor — Ruflo health check with auto-fix
3. rf-plugins — verify all 6 plugins are installed and active
4. mem-stats — memory system statistics
5. gitnexus status — verify knowledge graph integrity
6. bd ready --json — verify Beads is functional
7. hooks-route "test" — verify intelligence routing works
8. claude mcp list — verify all MCP servers registered

Report any issues and suggest fixes.
```

### Prompt: Clean Up and Optimize

```
Clean up the development environment:
1. wt-clean — prune stale worktrees
2. Compact AgentDB: remove old, low-value vectors
3. bd admin compact --analyze --json — check for compactable Beads issues
4. Clear cached MCP tool results
5. Run rf-doctor --fix for auto-repair
6. Verify all MCP servers are registered: claude mcp list
```

### Prompt: Dependency Update

```
Update [package] from [old version] to [new version]:
1. gnx-analyze — rebuild knowledge graph
2. Query GitNexus blast radius: what imports from this package?
3. Use Code Intelligence plugin to find deprecated API usage
4. wt-add dep-update-[package]
5. Update the dependency in package.json / requirements.txt / etc.
6. Fix all breaking changes across affected files
7. Run full test suite
8. aqe-generate + aqe-gate — verify all affected modules still work
9. Merge, wt-remove, gnx-analyze
10. bd create "Updated [package] [old] → [new]" -t task -p 2
```

### Prompt: Onboard a New Codebase

```
I just cloned [repo-url]. Onboard me completely:
1. Run devpods/setup.sh (or rf-init if TF already installed)
2. gitnexus analyze — build the knowledge graph
3. gitnexus wiki — generate repo documentation
4. gitnexus serve — start visual explorer so I can browse the graph
5. hooks-train — deep pretrain on the codebase
6. bd init — initialize Beads task tracker
7. bd ready --json — check for any existing tasks
8. neural-train — learn the codebase patterns
9. neural-patterns — show me what was learned
10. Use Code Intelligence plugin to identify: architecture patterns, 
    bounded contexts, technical debt, test coverage gaps
11. Generate a CLAUDE.md summarizing architecture, patterns, and conventions

Give me a summary of: architecture, dependencies, hot paths, and technical debt.
```

### Prompt: Start/Stop Background Services

```bash
rf-daemon              # Start Ruflo background workers (learning, optimization, security)
bd daemon start        # Start Beads auto-sync daemon
bd daemon stop         # Stop Beads daemon
bd daemon --status     # Check daemon health
```

### Prompt: Check and Manage Plugins

```bash
rf-plugins                                                    # List all installed plugins
npx ruflo@latest plugins install -n @claude-flow/plugin-agentic-qe     # Install a plugin
npx ruflo@latest plugins install -n @claude-flow/plugin-gastown-bridge  # Install Gastown
npx ruflo@latest plugins install -n @claude-flow/teammate-plugin        # Install Teammate
npx ruflo@latest plugins list                                             # List installed
```

### Prompt: Hive Mind / Advanced Swarm

```bash
# Initialize advanced hive-mind topology
npx ruflo hive-mind init --topology hierarchical-mesh --consensus byzantine
npx ruflo hive-mind spawn --agents 8 --strategy specialized

# Available consensus strategies:
# - raft: Leader-based, fault tolerance f < n/2
# - byzantine: BFT, untrusted environments, f < n/3
# - gossip: Epidemic spreading, eventual consistency
# - crdt: Conflict-free replicated data types, collaborative editing
```

### Prompt: Ruflo with Codex / Dual Mode

```bash
# Initialize for OpenAI Codex CLI (creates AGENTS.md instead of CLAUDE.md)
npx ruflo@latest init --codex

# Initialize for both Claude Code and Codex (dual mode)
npx ruflo@latest init --dual

# Full Codex setup with all 137+ skills
npx ruflo@latest init --codex --full
```

### Prompt: Worker Dispatch and Intelligence Metrics

```bash
# Dispatch background workers manually
npx ruflo worker dispatch --trigger audit --context "./src"
npx ruflo worker dispatch --trigger ultralearn --context "./src"
npx ruflo worker status

# View intelligence metrics
npx ruflo hooks metrics

# Pretrain (alias: hooks-train)
npx ruflo hooks pretrain

# Build optimized agent configurations from codebase analysis
npx ruflo hooks build-agents
```

### Prompt: LLM Provider Configuration

```
Configure Ruflo's LLM provider routing:
- Ruflo supports 6 LLM providers with automatic failover
- 4 load balancing strategies for cost/performance optimization
- 4 embedding providers (from 3ms local to cloud APIs)

Use the 3-tier model routing:
- Opus: architecture decisions, complex refactors, security analysis
- Sonnet: feature implementation, code review, documentation
- Haiku: test generation, linting, simple queries, boilerplate

Show me the current provider configuration and cost breakdown.
```

---

## 31. Compound Workflows — Real-World Scenarios

### Scenario: "I joined a new team and need to ship a feature this sprint"

```
Day 1 — Onboard:
1. Clone the repo, run devpods/setup.sh
2. gnx-analyze — build knowledge graph
3. gnx-wiki — generate repo documentation for myself
4. hooks-train — deep pretrain on codebase
5. bd init && bd-ready — load team's cross-session context
6. neural-patterns — understand conventions

Day 2 — Plan:
1. Generate PRD for the feature → plans/research/PLAN.md
2. aqe-gate — validate PRD
3. Review /plans/research → create ADR/DDD → do not implement
4. aqe-gate per ADR → aqe-gate on full plan
5. Update CLAUDE.md to match the DDD
6. bd-add — record my plan

Day 3-4 — Build:
1. wt-add feat-[name] — isolated worktree
2. rf-swarm — hierarchical swarm (architect + 2 coders + tester)
3. SPARC TDD — tests first, then implement
4. aqe-gate per bounded context
5. bd-add — record decisions as I go

Day 5 — Ship:
1. aqe-gate — full codebase quality check
2. Agent Teams review — 3 reviewers
3. gnx-analyze — blast radius
4. Create PR, address feedback, merge
5. bd-add — record completion and lessons learned
6. wt-remove feat-[name] — clean up
7. hooks post-task — train learning system
```

### Scenario: "Emergency production bug"

```
1. bd-ready — check if there's context about this area
2. gnx-analyze — trace execution path through dependency graph
3. wt-add hotfix-[ticket] — isolated worktree from production tag
4. hooks-route "debug [symptom description]" — route to best agent (Ruflo uses Opus)
5. Write failing test → diagnose → fix → test passes
6. aqe-gate — quality check (focused: tests for the bug + regression)
7. Create PR with minimal diff → merge immediately
8. bd-add — record root cause, fix, and prevention steps
9. wt-remove hotfix-[ticket]
10. hooks post-task — train learning system on the fix
11. Create follow-up ADR if systemic issue → aqe-gate on ADR
```

### Scenario: "Major version upgrade / dependency migration"

```
1. gnx-analyze — full dependency graph
2. Identify all affected files: GitNexus blast-radius for [dependency]
3. Create PRD: define target state, breaking changes, migration steps → plans/research/PLAN.md
4. Create ADR/DDD plan from PRD → aqe-gate per ADR
5. rf-mesh — mesh swarm with 4-6 coder agents:
   - Each handles a subsystem in its own worktree
   - Shared context via Beads
   - Consensus on shared interfaces via Teammate plugin
6. For each agent/worktree:
   - Update dependency
   - Fix breaking changes
   - Update tests
   - aqe-gate before merge
7. Merge in dependency order (bottom-up)
8. gnx-analyze after each merge
9. Final full QE: aqe-generate + aqe-gate
10. Performance comparison: before/after
11. bd-add — record the migration strategy for future reference
```

### Scenario: "Build a full application from scratch"

```
1. INITIALIZE:
   rf-wizard → bd init → os-init → Create dirs (src, tests, docs, scripts, config, plans)

2. PRD:
   Generate comprehensive PRD → plans/research/PLAN.md → aqe-gate

3. PLAN:
   Review /plans/research → create ADR/DDD → aqe-gate per ADR
   Update CLAUDE.md → update statusline → hooks-train → neural-train

4. SCAFFOLD (rf-swarm, hierarchical, 8 agents):
   Agent 1 (architect): project structure, configuration — does NOT write code
   Agent 2 (backend-coder): API, services, database
   Agent 3 (frontend-coder): UI, components, state management
   Agent 4 (auth-coder): authentication, authorization
   Agent 5 (tester): test suites for all layers — QA role
   Agent 6 (devops): CI/CD, Docker, deployment
   Agent 7 (documenter): API docs, README, architecture docs
   Agent 8 (security): security hardening, input validation

5. BUILD (iterative):
   - Each agent in its own worktree
   - SPARC TDD for all implementation
   - Beads for cross-agent coordination
   - AgentDB for pattern storage
   - aqe-gate per bounded context

6. VALIDATE:
   - aqe-gate: full codebase quality gate
   - gnx-analyze: dependency graph, no circular deps
   - Performance profiling (Perf Optimizer)
   - Security audit
   - Accessibility audit (UI UX Pro Max)

7. SHIP:
   - Agent Teams review
   - CI/CD pipeline green
   - Staging deployment + smoke tests
   - Production deployment
   - bd-add: record launch decisions and rollback plan
   - git tag -a v1.0.0
```

### Scenario: "Resume work / continue a build"

```
1. bd-ready — what's the project state?
2. mem-search "domain-model" — what does memory know?
3. gitnexus status — is the knowledge graph current?
4. Pick up the next bounded context from the plan
5. Follow the same protocol: wt-add → implement → aqe-gate → merge → gnx-analyze → bd-add
```

---

## 32. CLAUDE.md Customization Template

After Phase 1 planning, replace the generic CLAUDE.md with this structure:

```markdown
# CLAUDE.md — [Project Name]

## Project
[One paragraph: what this is, who it's for, why it exists]

## Bounded Contexts
- **[Context A]**: [responsibility] — [key aggregates]
- **[Context B]**: [responsibility] — [key aggregates]
- **[Context C]**: [responsibility] — [key aggregates]

## ADR Index
- ADR-001: [title] — [status]
- ADR-002: [title] — [status]

## Domain Language
- **[Term]**: [definition agents must follow]
- **[Term]**: [definition agents must follow]

## Memory Protocol
### Session Start
1. `bd-ready`
2. Review Native Tasks
3. AgentDB loads automatically

### Decision Tree
- Project decisions → `bd create "Decision: ..." -t task -p 2`
- Active work → Native Tasks
- Learned patterns → AgentDB (automatic)

## Isolation Rules
- [Context A] gets its own worktree when implementing
- [Context B] and [Context C] can share if no conflicts
- Always check GitNexus blast radius before editing: [list shared paths]

## Agent Teams
- Lead: architect role, max 3 teammates
- Roles needed: [backend, frontend, tester, etc.]
- Recursion depth: 2
- Deadlock: pause if 3+ blocked

## Model Routing
- Opus: [list what needs complex reasoning]
- Sonnet: [list standard implementation work]
- Haiku: [list simple tasks]

## Security
- [Project-specific security rules from ADRs]

## Hooks
- Pre-edit: [what to check before editing]
- Post-edit: [what to run after editing]

## Cost
- Session cap: $[amount]/hr
- Budget for this project: $[total]

## Stack
- [Framework, language, database, etc.]
- [Project-specific conventions]
```

---

## 33. Troubleshooting

| Problem | Fix |
|---------|-----|
| Commands not found | `source ~/.bashrc` |
| MCP servers not connected | `claude mcp list` — re-register with `claude mcp add ruflo -- npx -y ruflo@latest mcp start` |
| Old `cf-*` commands not working | Replaced by `rf-*` in v4.0 |
| Beads not initialized | `bd init` (requires git repo) |
| GitNexus not indexed | `gnx-analyze` from repo root |
| Ruflo not responding | `npx ruflo@latest init` then `rf-doctor` |
| Plugins not found | `rf-plugins` to check, reinstall with `npx ruflo@latest plugins install -n <name>` |
| Worktree conflicts | `wt-clean` to prune stale worktrees |
| Memory empty after restart | Beads persists in git — run `bd-ready`. AgentDB persists automatically. |
| Stale v3.x aliases in .bashrc | Setup script auto-cleans, or manually remove `# === TURBO FLOW` blocks |
| QE gate failing | Read the gap report. Fix gaps. Re-run. Don't skip. |
| Slash commands not working | Slash commands (`/sparc`, etc.) are gone in v4 — Ruflo auto-activates skills. Just describe what you want naturally. |

---

## 34. Quick Reference

### The Core Loop

```
BOOT:       source ~/.bashrc → rf-doctor (npx ruflo doctor --fix) → bd ready → gnx-analyze (npx gitnexus analyze) → hooks-train (npx ruflo hooks pretrain) → rf-daemon (npx ruflo daemon start) → turbo-status
PRD:        generate PRD → save to plans/research/PLAN.md → aqe-gate (npx ruflo@latest mcp call aqe/evaluate-quality-gate)
PLAN:       review /plans/research → create ADR/DDD → aqe-gate per ADR → aqe-gate on full plan
CUSTOMIZE:  update CLAUDE.md → update statusline → hooks-train → gnx-analyze → aqe-gate
EXECUTE:    rf-swarm (npx ruflo swarm init) → agents in worktrees (git worktree add) → aqe-gate per context → aqe-gate full codebase
FEATURE:    bd ready → blast radius → wt-add (git worktree add) → implement → aqe-gate → merge → gnx-analyze → bd create
REFACTOR:   characterization tests → wt-add → refactor → aqe-gate → merge → gnx-analyze → bd create
BUGFIX:     wt-add → failing test → fix → aqe-gate → merge → gnx-analyze → bd close
RELEASE:    full aqe-gate → security scan → changelog from bd list → git tag → bd create
HANDOFF:    bd create (remaining work) → bd close (done items) → gnx-analyze → neural-patterns (npx ruflo neural patterns)
```

### All Aliases → Native Commands

> **Note:** These are TurboFlow shell aliases defined in `devpods/setup.sh`. They wrap the native CLIs (`ruflo`, `bd`, `gitnexus`, `openspec`). If an alias doesn't work, use the native command directly.

| Alias | Native Command |
|-------|---------------|
| **Ruflo Orchestration** | |
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
| `rf-plugins` | `npx ruflo@latest plugins list` |
| **Memory** | |
| `mem-store KEY VALUE` | `npx ruflo@latest memory store --key "KEY" --value "VALUE"` |
| `mem-search QUERY` | `npx ruflo@latest memory search --query "QUERY"` |
| `mem-stats` | `npx ruflo@latest memory stats` |
| **Beads** | |
| `bd-ready` | `bd ready --json` |
| `bd-add` | `bd create "Title" -t task -p N` |
| `bd-list` | `bd list` |
| **Worktrees** | |
| `wt-add NAME` | `git worktree add .worktrees/NAME -b NAME-$(date +%s)` |
| `wt-remove NAME` | `git worktree remove .worktrees/NAME` |
| `wt-list` | `git worktree list` |
| `wt-clean` | `git worktree prune` |
| **GitNexus** | |
| `gnx-analyze` | `npx gitnexus analyze` |
| `gnx-serve` | `npx gitnexus serve` |
| `gnx-wiki` | `npx gitnexus wiki` |
| **Quality** | |
| `aqe-generate` | `npx @agentic-qe/v3 generate` |
| `aqe-gate` | `npx @agentic-qe/v3 gate` |
| **OpenSpec** | |
| `os-init` | `openspec init` |
| `os` | `openspec` |
| **Intelligence** | |
| `hooks-train` | `npx ruflo@latest hooks pretrain` |
| `hooks-route` | `npx ruflo@latest hooks route --task "..."` |
| `neural-train` | `npx ruflo@latest neural train` |
| `neural-patterns` | `npx ruflo@latest neural patterns` |
| **System** | |
| `turbo-status` | TF-specific (runs statusline check script) |
| `turbo-help` | TF-specific (prints all available commands) |

### Key MCP Tool Invocations

> **Prefix depends on registration:** Use `mcp__ruflo__` if you ran `claude mcp add ruflo ...`, or `mcp__claude-flow__` if registered as `claude-flow`. The Ruflo Wiki MCP Tools page lists all available tools and their parameters.

```
# Swarm
mcp__ruflo__swarm_init { topology: "hierarchical|mesh|ring|star" }
mcp__ruflo__agent_spawn { agentType: "coder|architect|tester|researcher|security|documenter|coordinator" }

# SPARC (invoked as Claude Code skills, not MCP tools)
# Use /sparc:tdd, /sparc:architect, /sparc:reviewer, etc.

# Memory
mcp__ruflo__memory_store { key: "...", value: "...", namespace: "..." }
mcp__ruflo__memory_search { query: "...", limit: N }

# Browser
mcp__ruflo__browser_open { url: "..." }
mcp__ruflo__browser_snapshot { interactive: true }
mcp__ruflo__browser_click { target: "@eN" }
mcp__ruflo__browser_fill { target: "@eN", value: "..." }
```

### Component Summary

| Category | Count |
|----------|-------|
| Ruflo Auto-Activated Skills | 36+ |
| Ruflo Plugins | 6 (QE, Code Intel, Test Intel, Perf, Teammate, Gastown) |
| Custom Skills | 1 (UI UX Pro Max) |
| Independent Tools | 2 (OpenSpec, GitNexus) |
| Memory Systems | 3 (Beads, Native Tasks, AgentDB) |
| MCP Tools | 215+ |
| Browser MCP Tools | 59 |
| Agents | 60+ |
| Hooks + Workers | 27 + 12 |
| **Total Components** | **23 integrated systems** |

---

*Generated for Turbo Flow v4.0 + Ruflo v3.5. Last updated: March 2026.*
}

# V4 Definitive Guide — Additions from TurboFlow Session

Apply these additions to the existing V4 Definitive Guide. Each section shows WHERE to insert and WHAT to add.

---

## 1. INSERT AFTER: Section 2 "Session Boot Sequence" (after "If anything fails, run rf-doctor...")

### Pre-Flight Checks (run before boot commands)

```bash
git stash list && git status --short          # forgotten stashes, uncommitted work
test -f .env || test -f .env.local || echo "⚠️  NO .env FILE"
npx prisma migrate status 2>/dev/null || echo "⚠️  Migrations pending"
df -h . | awk 'NR==2{if($5+0 > 90) print "⚠️  DISK " $5 " FULL"}'
```

### Post-Boot: Branch Analysis

After boot completes, run a full branch analysis to understand where you are:

```
Run a full branch analysis:
1. BRANCH STATE — ahead/behind main, diff summary, uncommitted, stashes, last 10 commits
2. CODEBASE CHANGES — gitnexus_detect_changes vs main, affected symbols/flows, risk level
3. BEADS STATUS — open issues, blockers, recently completed, flagged for human, bd lint
4. MEMORY RECALL — search memory + AgentDB for recent sessions, blockers, patterns, decisions
5. HEALTH CHECK — run tests, build, lint. Pending migrations? Missing env vars?
6. QUALITY ENGINEERING — aqe-gate, coverage gaps, security scan
7. GAP ANALYSIS — what's DONE, IN PROGRESS, NOT STARTED? What's blocking? What parallelizes?
Give me: A. Status summary (5-10 lines) B. Prioritized TodoWrite C. Session plan for 2-4 hours
```

### Status HUD

After every action response (file edit, bash, task completion, git op), end with a compact status block:

```
📍 Branch: feat/name · 3 files changed
🧠 Memory: Beads ✅ · HNSW ✅ · AgentDB ✅ · Context Autopilot ✅
🔧 Daemon: running · workers: map ✅ audit ✅ optimize ⏸
🧪 Tests: passing (42/42) · last run: 3m ago
💰 Cost: $2.34 · remaining: $12.66/hr
⚡ Model: Sonnet 4.5 (routed — confidence 0.87)
```

Show only active systems. On boot show full system table. On errors surface ⚠️ at top, auto-fix, proceed.

---

## 2. INSERT AS NEW SECTION: "2.5. Safety Protocols" (between Session Boot and Three-Tier Memory)

## 2.5. Safety Protocols

### Triple-Gate Merge Protocol

Any merge/rebase/push into `main` (or `master`/`production`/`prod`/`release`) requires **3 consecutive human confirmations** in separate prompt/response turns:

```
GATE 1 — "🔒 MERGE GATE 1/3: Merging [branch] → main. [changes summary, commit count, risk]. Confirm?"
GATE 2 — "🔒 MERGE GATE 2/3: Tests: [pass/fail]. Conflicts: [y/n]. Uncommitted: [y/n]. Confirm again?"
GATE 3 — "🔒 MERGE GATE 3/3: FINAL confirmation. Type 'yes' to execute."
```

Non-`yes` at any gate = immediate abort. Run `gitnexus_detect_changes` between gates 1–2. Sub-agents/swarm workers must escalate to lead agent. Hotfixes are NOT exempt.

**Does NOT apply to:** feature-to-feature merges, non-primary branch pushes, commits on any branch, branch/tag/worktree creation.

### Destructive Command Safeguards

One confirmation required before: `git reset --hard`, `rm -rf` (project dirs), `prisma migrate reset`, `DROP TABLE/DATABASE`, any `--force` that deletes data.

Format: `⚠️ DESTRUCTIVE: About to run [command]. This will [consequence]. Confirm?`

### Rollback Protocol

When a merge to main breaks things: `git revert --no-commit HEAD` → run tests → `git commit -m "revert: [reason]"` → `git push origin main` (skips Triple-Gate for emergency) → report to human → `bd create "[branch] merge reverted" -t bug -p 0 --json` → `ruv-remember "revert/[branch]" "root cause"`

### Conflict Resolution

Never silently auto-resolve merge conflicts. Simple (non-overlapping): resolve and show. Complex (overlapping logic): show both sides, ask the human. Always test + `gitnexus_detect_changes` after resolving.

### Non-Interactive Shell Commands

Always use force flags — aliased `-i` hangs agents indefinitely: `cp -f`, `mv -f`, `rm -f`, `rm -rf`, `cp -rf`. Also: `scp -o BatchMode=yes`, `apt-get -y`, `HOMEBREW_NO_AUTO_UPDATE=1 brew`.

### Escalation Rule

After 3 failed approaches to the same problem — STOP, explain what was tried, and ask the human. Don't burn tokens on attempt #4+.

---

## 3. REPLACE: Session Protocol "End" line in Section 3

FIND:
**End:** Close finished work → `bd close <id> --reason "..."` | Create tasks for remaining work → `bd ready --json` to verify state

REPLACE WITH:
**End:** Close finished work → `bd close <id> --reason "..."` | Create tasks for remaining work | Run quality gates (`npm test && npm run lint && npm run build`) | `bd dolt push` | `git pull --rebase && git push` (MANDATORY — work is NOT complete until push succeeds) | `bd ready --json` to verify state

---

## 4. INSERT AFTER: Section 7.3 "Parallel Implementation" (before Section 8)

### 7.4 — Batch Execution from ADR/DDD

After completing your ADR/DDD plan, execute all items sequentially without stopping between each:

```
Execute the following batch in order. For each item:
- Read relevant files, run gitnexus_impact on symbols you'll touch
- Implement the change with TDD
- Run tests after each item
- Log a bead (bd close or bd create for discovered work)
- Store patterns learned (ruv-remember)
- Show Status HUD after each item
- Do NOT stop between items — only stop if tests fail or you hit a blocker
- If an item fails, log it as a blocker bead and skip to next independent item
- aqe-gate after each bounded context completes

Summary at end: what completed, what failed, what needs attention.

BATCH:
1. [ADR-001] — [description]
2. [ADR-002] — [description]
3. [ADR-003] — [description]
...
```

**Short version:** `Execute all ready beads in dependency order. Don't stop between items. aqe-gate after each context. Summary at end.`

**From plan file:** `Read plans/research/PLAN.md. Execute every ADR in order as a batch. aqe-gate after each context. Summary at end.`

---

## 5. ADD TO: Section 11 "Beads" — Native CLI Commands (after `bd daemon stop`)

```bash
bd prime                         # Full workflow context dump (commands, session protocol)
bd remember KEY VALUE            # Persistent knowledge storage (NOT AgentDB — use for project facts)
bd defer <id>                    # Push issue to later
bd supersede <id>                # Mark as superseded
bd human <id>                    # Flag for human decision
bd stale                         # Find stale issues
bd orphans                       # Find orphaned issues
bd lint                          # Check data quality
bd formula list                  # Available workflow templates
bd mol pour <n>               # Execute a workflow
```

---

## 6. REPLACE: Section 11 "Cross-Session Handoff" prompt

FIND:
```
I'm ending this session. Before I go:
1. Create issues for remaining work...
...
4. Summarize what a new agent would need to know to continue
```

REPLACE WITH:
```
I'm ending this session. Before I go:
1. Create issues for remaining work:
   bd create "Continue [task description]" -p 1 -t task
   bd create "Investigate [open question]" -p 2 -t task
2. Close completed tasks:
   bd close <id> --reason "Completed: [summary]"
3. Run quality gates: npm test && npm run lint && npm run build
4. gnx-analyze — update graph
5. neural-patterns — capture what was learned
6. MANDATORY PUSH:
   bd dolt push && git pull --rebase && git push
   git status  # MUST show "up to date with origin"
7. Summarize what a new agent would need to know to continue
Work is NOT complete until git push succeeds.
```

---

## 7. ADD TO: Section 33 "Troubleshooting" table

| Agent hangs on shell command | Use `-f` flags: `cp -f`, `mv -f`, `rm -f` — aliased `-i` causes hangs |
| Merge to main blocked | Triple-Gate requires 3 human confirmations — this is by design |
| Work lost after session | Session end protocol requires `git push` — check `git status` |
| AgentDB returns unavailable | `npm install -g @claude-flow/memory && npx ruflo@latest doctor --fix` |
| Agent spinning on same problem | 3-strikes rule: after 3 failed attempts it should stop and ask you |

---

## 8. ADD TO: Section 10 "Git Worktrees" — after "Agent Roles" table

### Merge Protocol for Worktrees

When merging worktree branches:
- **To feature branch:** merge directly, no special protocol
- **To main:** Triple-Gate required for EACH merge
- **Test BEFORE merging** — run tests on the feature branch first
- **`wt-clean` is MANDATORY after merge** — not optional cleanup
- **Conflicts:** never auto-resolve silently, show both sides for complex conflicts

---

## 9. UPDATE: Table of Contents

Add after entry 2:
```
2.5. [Safety Protocols](#25-safety-protocols)
```

Add after entry 7.3 within section 7:
```
7.4. [Batch Execution from ADR/DDD](#74--batch-execution-from-adrddd)
```
