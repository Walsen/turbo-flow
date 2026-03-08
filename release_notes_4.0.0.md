# TurboFlow 4.0.0 Release Notes — The Ruflo Migration

**Release Date:** March 7, 2026
**Previous Version:** v3.4.1 (February 2025)

---

## Summary

TurboFlow 4.0 is a complete rebuild. Claude Flow graduated to Ruflo v3.5 after 5,800 commits and a rename. Every package reference, alias, and integration point in TurboFlow has been rewritten to match. The setup script went from 15 steps installing ghost packages to 10 steps installing what actually exists.

Three new systems fill gaps that v3.x never addressed: Beads gives agents memory that survives between sessions, GitNexus gives agents structural awareness of the codebase before they touch it, and native git worktrees give each parallel agent its own isolated workspace.

---

## By the Numbers

| Metric | v3.4.1 | v4.0.0 |
|--------|--------|--------|
| Setup steps | 15 | 10 |
| Setup script lines | ~500 | 771 |
| Core packages to install | 4 separate | 1 (Ruflo bundles all) |
| MCP tools | 175+ | 215+ |
| Agents | 60+ | 60+ |
| Plugins | 15 | 6 |
| Cross-session memory | None | Beads (git-native JSONL) |
| Agent isolation | None | Git worktrees + PG Vector schema namespacing |
| Codebase awareness | None | GitNexus knowledge graph + MCP |
| Model routing | Manual | Ruflo 3-tier auto-routing (~75% cost savings) |
| Browser automation | Playwright MCP + Chrome DevTools MCP | Bundled in Ruflo (59 MCP tools) |
| Observability | agtrace (separate install) | Bundled in Ruflo |
| Post-setup verification | 15 steps | 13 steps |

---

## What's New

### Ruflo v3.5 (replaces Claude Flow)

The core orchestration layer is now a single `npx ruflo@latest init` command. This one install replaces four separate v3.x packages: `claude-flow@alpha`, `@ruvector/cli`, `@ruvector/sona`, and `@claude-flow/browser`. Ruflo v3.5 bundles AgentDB v3 with 8 new controllers, RuVector with WASM acceleration, SONA, 215 MCP tools, 60+ agents, a skills-based system (replacing slash commands), 3-tier intelligent model routing, 59 browser automation MCP tools, and built-in observability.

All `cf-*` aliases are replaced by `rf-*` aliases.

### Beads — Cross-Session Project Memory

Agents now remember across sessions. Beads stores issues, decisions, and blockers as git-native JSONL files. The CLAUDE.md template includes a mandatory memory protocol: `bd ready` at session start, `bd add` during work, and automatic AgentDB persistence at session end. This is the three-tier memory system the v3.x PRD called for but never shipped.

### GitNexus — Codebase Knowledge Graph

Before agents edit shared code, they can now check the blast radius. GitNexus indexes your repo into a knowledge graph of dependencies, call chains, and execution flows. It runs as an MCP server so Claude Code agents get these tools natively. The `wt-add` worktree helper auto-indexes new worktrees in the background.

### Native Git Worktree Helpers

Each parallel agent now operates in its own git worktree with automatic PG Vector schema namespacing. Four bash functions handle the lifecycle: `wt-add` creates an isolated worktree with a timestamped branch and auto-indexes with GitNexus, `wt-remove` cleans up, `wt-list` shows active worktrees, and `wt-clean` prunes stale ones.

### Native Agent Teams

Anthropic's experimental `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is enabled by default. The CLAUDE.md template sets guardrails: max 3 teammates per lead agent, recursion depth of 2, and a deadlock detection policy (pause and alert human if 3+ agents are blocked simultaneously).

### UI UX Pro Max Skill

The design system skill from v3.x is preserved. Installed via `npx uipro-cli init --ai claude --offline`, it provides component patterns, accessibility guidance, responsive layouts, and design tokens as a Claude Code skill.

### Statusline Pro v4.0

The powerline-style status bar is updated with TurboFlow 4.0 branding. Three lines showing project name, model, git branch, TF version, session ID, token usage with context window bar, cache hit percentage, cost, duration, and lines changed.

### OpenSpec

Spec-driven development via `@fission-ai/openspec` is kept as an independent npm package with `os` and `os-init` aliases.

---

## What Changed

### Plugins: 15 → 6

Nine plugins were removed. Six were redundant with capabilities Ruflo v3.5 now bundles natively. Three were domain-specific and not relevant.

**Kept (6):**
- Agentic QE — 58 QE agents, TDD, coverage, security scanning, chaos engineering
- Code Intelligence — code analysis, pattern detection, refactoring
- Test Intelligence — test generation, gap analysis, flaky test detection
- Perf Optimizer — performance profiling, bottleneck detection
- Teammate Plugin — bridges Agent Teams with Ruflo swarms (21 MCP tools)
- Gastown Bridge — WASM-accelerated orchestration, Beads sync (20 MCP tools)

**Removed — redundant with Ruflo v3.5 core (6):**
- cognitive-kernel → Ruflo's ReasoningBank and guidance control plane
- hyperbolic-reasoning → RuVector WASM hyperbolic embeddings
- quantum-optimizer → Ruflo's EWC++ consolidation and RVFOptimizer
- neural-coordination → Ruflo's native swarm coordination
- prime-radiant → niche mathematical interpretability
- ruvector-upstream → RuVector is bundled directly in Ruflo v3.5

**Removed — domain-specific (3):**
- healthcare-clinical (HIPAA/FHIR)
- financial-risk (PCI-DSS/SOX)
- legal-contracts

### Standalone Tools Removed

These were installed separately in v3.x but are now either bundled in Ruflo or redundant:

| Tool | v3.x | v4.0 Replacement |
|------|------|-------------------|
| `claude-flow@alpha` | npm global | Ruflo v3.5 |
| `@ruvector/cli` | npm global | Bundled in Ruflo |
| `@ruvector/sona` | npm global | Bundled in Ruflo |
| `@claude-flow/browser` | npm global | Bundled in Ruflo (59 MCP tools) |
| `agentic-jujutsu` | npm global | Bundled in Ruflo |
| `claudish` | npm global | Ruflo 3-tier model routing |
| `specify-cli` (Spec-Kit) | npm global | Ruflo SPARC skill |
| `agtrace` | npm global | Ruflo built-in observability |
| PAL MCP | git clone + uv | Ruflo model routing |
| `agent-browser` | npm global | Bundled in Ruflo |
| `security-analyzer` | git clone skill | Ruflo skill |
| `worktree-manager` | git clone skill | Native `wt-*` bash functions |
| `uv` | Python package manager | No longer needed (PAL MCP removed) |
| `sql.js` | npm local | Handled by Ruflo |
| `ccusage` | npm global | `claude-usage` alias or Ruflo statusline |
| HeroUI + Tailwind + TypeScript | npm local scaffold | Removed (out of scope) |

### Aliases Rewritten

All `cf-*` aliases are replaced by `rf-*`. All plugin-specific aliases (`plugin-qe`, `plugin-cognitive`, etc.) are replaced by `aqe-*` for QE and Ruflo-native commands for the rest. New alias families added: `bd-*` (Beads), `wt-*` (worktrees), `gnx-*` (GitNexus), `hooks-*` (intelligence), `neural-*` (neural), `mem-*` (memory).

Old v3.x alias blocks in `.bashrc` are automatically cleaned up by the setup script.

### CLAUDE.md Rewritten

The workspace context file is completely new. It includes the three-tier memory protocol with a decision tree, isolation rules, Agent Teams guardrails, model routing tiers, plugin reference, GitNexus usage instructions, and cost guardrails. References to removed tools (Claudish, Ars Contexta, OpenClaw, etc.) are gone.

---

## Migration Guide

### From v3.4.1

1. Run `setup-turboflow-4.sh` — it handles everything including cleanup of old aliases
2. Your old `cf-*` commands become `rf-*`
3. Slash commands (`/sparc`, etc.) are gone — Ruflo auto-activates skills based on your task
4. Run `bd init` in your project repos to enable Beads memory
5. Run `npx gitnexus analyze` in your repos to build the codebase knowledge graph
6. The `v3/` directory in the repo preserves everything — nothing was deleted

### Alias Mapping

| v3.4.1 | v4.0.0 |
|--------|--------|
| `cf` | `rf` |
| `cf-init` | `rf-init` |
| `cf-swarm` | `rf-swarm` |
| `cf-mesh` | `rf-mesh` |
| `cf-doctor` | `rf-doctor` |
| `cf-daemon` | `rf-daemon` |
| `cf-mcp` | Automatic via `rf-wizard` |
| `cf-memory` | `mem-search`, `mem-store`, `mem-stats` |
| `cf-plugins` | `rf-plugins` |
| `cfb-open` | Via Ruflo browser MCP tools |
| `plugin-qe` | `aqe-generate`, `aqe-gate` |
| `wt-status` | `wt-list` |
| `wt-create` | `wt-add` |
| No equivalent | `bd-ready`, `bd-add` (Beads) |
| No equivalent | `gnx-analyze` (GitNexus) |
| No equivalent | `hooks-train`, `hooks-route` |

---

## Repository Structure

```
turbo-flow/
├── v3/                          ← archived v3.0-v3.4.1 (Claude Flow era)
├── v4/                          ← active development (Ruflo era)
│   ├── .devcontainer/
│   │   ├── devcontainer.json
│   │   ├── setup-turboflow-4.sh       (771 lines, 10 steps)
│   │   └── post-setup-turboflow-4.sh  (488 lines, 13 checks)
│   ├── scripts/
│   │   └── generate-claude-md.sh
│   ├── CLAUDE.md
│   └── README.md
├── docs/
│   ├── migration-v3-to-v4.md
│   └── release-notes-v4.0.0.md
├── CLAUDE.md                    ← root, points to v4/
└── README.md
```

---

## Component Inventory (23 Total)

| # | Component | Source | New in 4.0 |
|---|-----------|--------|------------|
| 1 | build-essential + python3 + git + curl + jq | apt | — |
| 2 | Node.js 20+ | nvm/nodesource | Updated from 18+ |
| 3 | Claude Code | npm | — |
| 4 | Ruflo v3.5 | npx | Replaces claude-flow |
| 5 | Ruflo MCP registration | claude mcp add | Replaces claude-flow MCP |
| 6 | Ruflo doctor | npx | Replaces cf-doctor |
| 7 | Plugin: Agentic QE | ruflo plugins | — |
| 8 | Plugin: Code Intelligence | ruflo plugins | — |
| 9 | Plugin: Test Intelligence | ruflo plugins | — |
| 10 | Plugin: Perf Optimizer | ruflo plugins | — |
| 11 | Plugin: Teammate | ruflo plugins | — |
| 12 | Plugin: Gastown Bridge | ruflo plugins | — |
| 13 | OpenSpec | npm global | — |
| 14 | UI UX Pro Max skill | uipro-cli | — |
| 15 | GitNexus | npm global | ⭐ New |
| 16 | GitNexus MCP registration | npx gitnexus setup | ⭐ New |
| 17 | Beads | npm global | ⭐ New |
| 18 | Native Agent Teams | env var | ⭐ New |
| 19 | Workspace directories | mkdir | — |
| 20 | Statusline Pro v4.0 | bash script | Updated |
| 21 | CLAUDE.md template | generated | Rewritten |
| 22 | Bash aliases (50+) | .turboflow_aliases | Rewritten |
| 23 | Git worktree helpers | bash functions | ⭐ New |

---

## Known Issues

- Ruflo's `--wizard` flag may fall back to non-interactive `init` in headless environments (DevPod, Codespaces). This is handled by the setup script.
- The `npx ruflo@latest plugins install -n` flag may need `--name` on some versions. The setup script tries both.
- Beads `bd init` requires the workspace to be a git repository.
- GitNexus indexing runs in the background on `wt-add` — large repos may take a moment.

---

## What's Next

- **v4.1**: OpenFang Hands integration — autonomous agents for research, lead gen, social posting, competitor monitoring per business entity
- **v4.2**: Open WebUI 4-instance deployment automation (Rackspace Spot)
- **v4.3**: Per-entity CLAUDE.md and knowledge base customization

---

*"The tools change. The composition survives. The businesses run."*
