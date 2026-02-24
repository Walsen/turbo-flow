# Turbo Flow v3.4.1 — Workflow Guide

## What's Installed

| Layer | Components |
|-------|------------|
| **Orchestration** | Claude Code, Claude Flow V3 (daemon, swarm, MCP, browser) |
| **Memory** | Claude Flow SQLite memory, AgentDB vector DB (HNSW), sql.js |
| **Intelligence** | RuVector neural engine, hooks intelligence, neural operations |
| **Native Skills** | 36 skills built-in to Claude Flow (Core, AgentDB, GitHub, V3 Dev, ReasoningBank, Flow Nexus, Additional) |
| **Plugins** | 15 plugins: QE (2), Code Intel (1), Cognitive (2), Performance (3), Neural (2), Domain (3), Infrastructure (2) |
| **Custom Skills** | Security Analyzer, UI UX Pro Max, Worktree Manager |
| **Quality** | Agentic QE (test gen + quality gates), Test Intelligence |
| **Ecosystem** | OpenSpec (API design), RuVector RUVLLM, RuV Helpers 3D Visualization |
| **Monitoring** | Statusline Pro, ccusage (on-demand) |

---

## Core Philosophy: ADR + DDD First

Turbo Flow v3.4.1 is built around **Architecture Decision Records (ADR)** and **Domain-Driven Design (DDD)** as the primary development methodology.

- **Architecture decisions are documented and traceable** via ADRs
- **Code organization reflects business domains** via DDD bounded contexts
- **Ubiquitous language emerges from domain modeling**
- **Strategic design guides tactical implementation**

---

## Boot Sequence

This is the correct startup order. Each step depends on the one before it.

### Step 1 — Initialize Claude Flow

This creates the `.claude-flow/` workspace config and `.swarm/` directory.

```bash
cf-init
```

> "Initialize Claude Flow in this workspace with default settings"

Use `cf-wizard` for guided setup, or `cf-init` for defaults.

### Step 2 — Verify Environment

```bash
cf-doctor
```

> "Run Claude Flow doctor to check that everything is healthy"

Fix any issues before proceeding.

### Step 3 — Initialize Memory

Claude Flow's memory is SQLite-based at `.swarm/memory.db`.

```bash
npx -y claude-flow@alpha memory init
```

Configure retention and limits:

```bash
npx -y claude-flow@alpha config set memory.retention 30d
npx -y claude-flow@alpha config set memory.maxSize 1GB
```

### Step 4 — Register MCP Servers

```bash
claude mcp add claude-flow -- npx -y claude-flow@alpha mcp start
```

Verify:

```bash
claude mcp list
```

### Step 5 — Activate RuVector Hooks

```bash
ruv-init
```

For existing projects, pretrain from the codebase:

```bash
hooks-train
```

### Step 6 — Start the Daemon

```bash
cf-daemon
```

### Step 7 — Verify Everything

```bash
turbo-status
mem-stats
hooks-intel
claude mcp list
```

**You're now fully booted.**

---

## Boot Sequence (Quick Copy-Paste)

```bash
source ~/.bashrc
cf-init
cf-doctor
npx -y claude-flow@alpha memory init
npx -y claude-flow@alpha config set memory.retention 30d
claude mcp add claude-flow -- npx -y claude-flow@alpha mcp start
ruv-init
hooks-train
cf-daemon
turbo-status
```

---

## Three Memory Systems

| System | What it does | How to use |
|--------|-------------|------------|
| **Claude Flow Memory** (mem-*) | Key-value + vector search in SQLite | `mem-store`, `mem-search`, `mem-vsearch` |
| **RuVector** (ruv-*) | Neural pattern learning | `ruv-remember`, `ruv-recall`, `ruv-route` |
| **AgentDB** (agentdb-*) | Standalone HNSW vector database | `agentdb-store`, `agentdb-query` via MCP |

### When to use which:

- **Storing project configuration or task state** → Claude Flow memory (`mem-store`)
- **Remembering a coding pattern that worked** → RuVector (`ruv-remember`)
- **Storing documents for semantic RAG search** → AgentDB (via MCP tools)
- **Finding which agent is best for a task** → RuVector routing (`ruv-route`)
- **Searching memory by keyword** → Claude Flow (`mem-search`)
- **Searching memory by meaning** → AgentDB or Claude Flow (`mem-vsearch`)

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

**Creating an ADR:**

> "Create an ADR for adopting PostgreSQL as our primary database"

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

---

## Native Skills (36 Built-in)

> **IMPORTANT:** These skills are **built-in to Claude Flow**. They are NOT installed via a command. They are available automatically when Claude Flow is initialized.

### Core Skills (6)

| Skill | Purpose |
|-------|---------|
| `sparc-methodology` | SPARC development methodology |
| `swarm-orchestration` | Multi-agent coordination |
| `github-code-review` | AI-powered PR reviews |
| `agentdb-vector-search` | HNSW vector search |
| `pair-programming` | Driver/Navigator AI coding |
| `hive-mind-advanced` | Queen-led collective intelligence |

### AgentDB Skills (4)

| Skill | Purpose |
|-------|---------|
| `agentdb-advanced` | QUIC sync, multi-database |
| `agentdb-learning` | 9 RL algorithms |
| `agentdb-memory-patterns` | Session memory, patterns |
| `agentdb-optimization` | Quantization, HNSW |

### GitHub Skills (4)

| Skill | Purpose |
|-------|---------|
| `github-multi-repo` | Cross-repo coordination |
| `github-project-management` | Issues, project boards |
| `github-release-management` | Versioning, deployment |
| `github-workflow-automation` | CI/CD automation |

### V3 Development Skills (9)

| Skill | Purpose |
|-------|---------|
| `v3-cli-modernization` | Interactive prompts |
| `v3-core-implementation` | DDD domains, clean architecture |
| `v3-ddd-architecture` | Bounded contexts, microkernel |
| `v3-integration-deep` | Deep agentic-flow integration |
| `v3-mcp-optimization` | Sub-100ms MCP response |
| `v3-memory-unification` | Unified AgentDB backend |
| `v3-performance-optimization` | Flash Attention |
| `v3-security-overhaul` | CVE remediation |
| `v3-swarm-coordination` | 15-agent hierarchical mesh |

### ReasoningBank Skills (2)

| Skill | Purpose |
|-------|---------|
| `reasoningbank-agentdb` | Trajectory tracking |
| `reasoningbank-intelligence` | Pattern recognition |

### Flow Nexus Skills (3)

| Skill | Purpose |
|-------|---------|
| `flow-nexus-neural` | Neural network training |
| `flow-nexus-platform` | Auth, sandboxes, deployment |
| `flow-nexus-swarm` | Cloud-based swarm deployment |

### Additional Skills (8)

| Skill | Purpose |
|-------|---------|
| `agentic-jujutsu` | Quantum-resistant version control |
| `hooks-automation` | Pre/post task hooks |
| `performance-analysis` | Bottleneck detection |
| `skill-builder` | Create custom skills |
| `stream-chain` | Multi-agent streaming |
| `swarm-advanced` | Advanced distributed workflows |
| `verification-quality` | Truth scoring, rollback |
| `dual-mode` | Dual-mode operations |

---

## Plugins (15 Total)

### Quality Engineering Plugins (2)

| Plugin | Purpose |
|--------|---------|
| `agentic-qe` | Autonomous quality engineering, test generation |
| `test-intelligence` | Smart test selection, coverage optimization |

### Code Intelligence Plugins (1)

| Plugin | Purpose |
|--------|---------|
| `code-intelligence` | AST analysis, code understanding |

### Cognitive Plugins (2)

| Plugin | Purpose |
|--------|---------|
| `cognitive-kernel` | Meta-cognition, self-reflection |
| `hyperbolic-reasoning` | Hyperbolic geometry for reasoning |

### Performance Plugins (3)

| Plugin | Purpose |
|--------|---------|
| `perf-optimizer` | Performance profiling |
| `quantum-optimizer` | Quantum-inspired optimization |
| `prime-radiant` | Predictive performance modeling |

### Neural Plugins (2)

| Plugin | Purpose |
|--------|---------|
| `neural-coordination` | Multi-agent neural coordination |
| `ruvector-upstream` | Direct RuVector integration |

### Domain-Specific Plugins (3)

| Plugin | Purpose |
|--------|---------|
| `financial-risk` | Financial modeling, risk assessment |
| `healthcare-clinical` | Clinical workflows |
| `legal-contracts` | Contract analysis |

### Infrastructure Plugins (2)

| Plugin | Purpose |
|--------|---------|
| `gastown-bridge` | WASM bridge |
| `teammate-plugin` | Team collaboration |

---

## Workflow 1: New Builds (ADR + DDD)

### 1. Boot

> "Check system status and make sure daemon is running"

### 2. Domain Discovery

> "Analyze these business requirements and identify potential bounded contexts"

> "Use v3-ddd-architecture to discover domains"

### 3. Architecture Decision Records

> "Create ADR-001 documenting our architecture decisions"

### 4. Domain Modeling

> "Design aggregates, entities, and value objects for the Identity bounded context"

### 5. Build

> "Spawn a hierarchical swarm with a system architect and implementers"

### 6. Test & Secure

> "Generate comprehensive tests targeting 95% coverage"

> "Run plugin-qe for autonomous quality engineering"

### 7. Deploy

> "Deploy this to Vercel and give me the preview URL"

### 8. Document & Learn

```bash
ruv-learn
ruv-stats
mem-stats
```

---

## Workflow 2: Continued Builds

### 1. Recover Context

> "Recall what RuVector knows about this project"

```bash
cf-doctor
ruv-recall "domain-model"
mem-search "adr"
```

### 2. Analyze Impact

> "Analyze the impact of adding a Payment bounded context"

### 3. Design the Extension

> "Design the Payment bounded context with aggregates and domain events"

### 4. Build & Test

> "Create a feature swarm with 2 backend devs and a tester"

---

## Workflow 3: Refactor Builds

### 1. Baseline

> "Recall all ADRs and the current domain model"

> "Generate characterization tests"

### 2. Plan the Evolution

> "Create ADR for migrating to modular monolith with DDD"

### 3. Execute Refactoring

> "Use v3-core-implementation patterns to refactor"

### 4. Validate

> "Run characterization tests against refactored code"

---

## Tool Reference

### Swarm Topologies

| Topology | Command | When to use |
|----------|---------|-------------|
| Hierarchical | `cf-swarm` | Domain implementation |
| Mesh | `cf-mesh` | Refactoring, parallel work |

### Claude Flow Browser (59 MCP Tools)

| Command | What it does |
|---------|-------------|
| `cfb-open <url>` | Open a page |
| `cfb-snap` | Take a snapshot |
| `cfb-click <ref>` | Click element |
| `cfb-fill <ref> <val>` | Fill an input |
| `cfb-trajectory` | Start recording |
| `cfb-learn` | Save the recording |

### Memory Operations

**Claude Flow Memory:**

| Command | What it does |
|---------|-------------|
| `mem-store "key" "value"` | Store data |
| `mem-search "query"` | Keyword search |
| `mem-vsearch "query"` | Semantic search |
| `mem-stats` | Database statistics |

**RuVector:**

| Command | What it does |
|---------|-------------|
| `ruv-init` | Activate hooks |
| `ruv-remember "pattern"` | Save patterns |
| `ruv-recall "query"` | Retrieve patterns |
| `ruv-route "task"` | Route to best agent |
| `ruv-learn` | Consolidate learnings |
| `ruv-stats` | Learning statistics |

### Plugin Quick Reference

| Category | Commands |
|----------|----------|
| **Quality** | `plugin-qe`, `plugin-test-intel` |
| **Code Intel** | `plugin-code-intel` |
| **Cognitive** | `plugin-cognitive`, `plugin-hyperbolic` |
| **Performance** | `plugin-perf`, `plugin-quantum`, `plugin-prime` |
| **Neural** | `plugin-neural` |
| **Domain** | `plugin-financial`, `plugin-healthcare`, `plugin-legal` |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Commands not found | `source ~/.bashrc` |
| MCP servers not connected | `claude mcp list` — re-register |
| Memory empty after restart | `npx -y claude-flow@alpha memory init` |
| RuVector not learning | `ruv-init` then `hooks-train` |
| Skills not available | Skills are built-in - just use `cf` commands |
| Plugin not found | `cf-plugins list` to check installed plugins |

---

## Quick Reference

```
BOOT:       cf-init → memory init → mcp add → ruv-init → hooks-train → cf-daemon
DISCOVER:   v3-ddd-architecture → identify bounded contexts
DECIDE:     create ADRs → store in memory
MODEL:      aggregates → entities → value objects
BUILD:      v3-core-implementation → swarm orchestrate
TEST:       plugin-qe → plugin-test-intel → aqe-gate
SECURE:     v3-security-overhaul → scan vulnerabilities
DEPLOY:     deploy-preview → cf-gh-release
LEARN:      ruv-remember → ruv-learn
MONITOR:    turbo-status → cf-doctor → ccusage
```

---

## Skills & Plugins Summary

| Category | Count | Notes |
|----------|-------|-------|
| Native Skills | 36 | Built-in to Claude Flow |
| Custom Skills | 3 | Security Analyzer, UI UX Pro Max, Worktree Manager |
| **Plugins** | **15** | Install via `cf-plugins install -n <name>` |
| **Total** | **54** | Complete agentic development environment |
