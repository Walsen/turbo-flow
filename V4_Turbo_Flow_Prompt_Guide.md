# TurboFlow 4.0 — Prompt Guide

This guide follows the actual TurboFlow development workflow: plan with ADR/DDD, customize the environment, then swarm-implement. Every prompt maximizes the 24 TurboFlow features.

Validated against: Anthropic's 2026 Agentic Coding Trends Report, PACT framework for Agentic QE, DDD-for-multi-agent-systems research (Croft 2025, TechInContext 2025), Claude Code swarm best practices, and ADR community practices (adr.github.io).

---

## How This Works

The core loop is 3 phases:

1. **Plan** — ADR/DDD from research, using Ruflo's self-learning, hooks, security, and optimizations. Swarm plans but does NOT implement.
2. **Customize** — Update CLAUDE.md and statusline to match the DDD you just outlined. This is how agents know your project.
3. **Execute** — Swarm implements completely: code, test, validate, benchmark, optimize, document. Continue until done.

**After every phase and every ADR completion**, the Agentic QE plugin runs the complete QE agent pipeline (`aqe-generate` → `aqe-gate`) to verify the output and identify gaps before proceeding. No phase is considered complete until QE passes.

Everything else (troubleshooting, refactoring, features, gitops) follows the same pattern with variations.

### Key Principles (from research)

- **Plan cheap, execute expensive** — Phase 1 uses minimal tokens to plan. Phase 3 uses swarms for parallel execution. This matches Anthropic's recommended pattern.
- **One bounded context per agent** — DDD research confirms: each agent should own a single bounded context with clear boundaries. Agents crossing context boundaries cause drift and merge conflicts.
- **Worktree isolation is mandatory** — Every serious multi-agent framework converges on git worktrees. No shared working directory between parallel agents. Ever.
- **QE gates are phase transitions, not just end-of-line checks** — The PACT framework (Proactive, Autonomous, Collaborative, Targeted) recommends quality gates at every phase boundary, not just before release. This catches architectural gaps before they become implementation bugs.
- **CLAUDE.md is your operating system** — It's not documentation. It's the instruction set every agent reads before doing anything. A generic CLAUDE.md produces generic work. A project-specific CLAUDE.md produces project-aligned work.
- **Beads + ADRs = institutional memory** — Decisions recorded in Beads survive sessions. ADRs survive team changes. Together they prevent the "why did we do this?" problem that kills projects at month 3.

---

## Phase 0: Session Boot

Every session. No exceptions.

```bash
source ~/.bashrc
bd-ready              # Load project state from last session
gnx-status            # Is the knowledge graph current?
turbo-status          # Full stack health check
```

First time on a new project:

```bash
rf-init               # Initialize Ruflo
gnx-analyze           # Build codebase knowledge graph
bd init               # Initialize Beads memory
hooks-train           # Pretrain Ruflo on this codebase
```

---

## Phase 1: Plan (ADR/DDD)

### 1.1 — Research-Driven ADR/DDD Planning

This is the core planning prompt. It reads your research, creates the full architecture plan, and uses every Ruflo intelligence feature — but does NOT implement.

> Review the `/plans/research` and create a detailed ADR/DDD implementation using all the various capabilities of Ruflo self-learning, security, hooks, and other optimizations. Spawn swarm, do not implement yet.
>
> Specifically:
>
> **ADR Requirements:**
> - Create ADRs in `docs/adr/` for every architectural decision
> - Each ADR must reference which Ruflo capabilities it leverages (hooks, security scanning, model routing, AgentDB patterns, etc.)
> - Include cost/complexity estimates per bounded context using the 3-tier model routing (Opus/Sonnet/Haiku)
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
> **QE Gate (mandatory after each ADR and after full plan):**
> - After each ADR is written, run the Agentic QE pipeline to verify the ADR is complete, consistent with other ADRs, and has no gaps in reasoning or missing dependencies
> - After the full DDD plan is complete, run the complete QE agent pipeline across all ADRs and the domain map to identify: missing bounded contexts, undefined integration points, security gaps, untestable designs, and missing acceptance criteria
> - Do NOT proceed to implementation until QE passes with no critical gaps
>
> **ADR Definition of Done (each ADR must have all 5):**
> 1. **Evidence** — data or research supporting the decision
> 2. **Criteria & Alternatives** — what was considered and why alternatives were rejected
> 3. **Agreement** — explicit status (proposed/accepted/deprecated/superseded)
> 4. **Documentation** — stored in `docs/adr/` and recorded in Beads
> 5. **Realization Plan** — how this decision maps to bounded contexts and implementation tasks
>
> Do NOT implement any code. Plan only.

After this runs, verify and record:

```bash
aqe-generate           # Generate validation checks for the plan
aqe-gate               # Quality gate — must pass before proceeding
bd add --type decision "ADR/DDD plan complete — [N] bounded contexts, [N] ADRs — QE passed"
gnx-analyze
```

### 1.2 — Variations

**For an API-heavy project, add:**

> Also create an API specification covering all endpoints identified in the bounded contexts. Define request/response schemas, auth requirements, rate limits, and error contracts.

**For a UI-heavy project, add:**

> Also define the component architecture using UI UX Pro Max patterns. Map each bounded context to its UI surface: pages, components, design tokens, accessibility requirements.

**For a data-heavy project, add:**

> Also define the data architecture: schemas, migrations, indexes, replication strategy, backup policy. Map each bounded context to its data store and specify cross-context query patterns.

---

## Phase 2: Customize the Environment

After planning, you MUST customize CLAUDE.md and the statusline to match your project. This is how agents know what they're working on.

### 2.1 — Customize CLAUDE.md

> Update the CLAUDE.md to match the DDD we just outlined. Replace the generic template with project-specific context:
>
> - **Identity**: What this project is, its business purpose, target users
> - **Bounded Contexts**: List all contexts from our DDD, their responsibilities, and boundaries
> - **ADR Index**: Reference all ADRs by number with one-line summaries
> - **Domain Language**: Ubiquitous language glossary — terms agents must use correctly
> - **Memory Protocol**: Keep the 3-tier protocol but add project-specific Beads categories (e.g., "API decisions", "schema changes", "deployment configs")
> - **Isolation Rules**: Keep the worktree rules but specify which contexts get their own worktrees
> - **Agent Teams Rules**: Specify which agent roles this project needs (architect, backend, frontend, tester, etc.)
> - **Model Routing**: Specify which parts of this project need Opus vs Sonnet vs Haiku
> - **GitNexus Checkpoints**: List the shared code paths where agents MUST check blast radius before editing
> - **Security Requirements**: Project-specific security rules from the ADRs
> - **Hooks Configuration**: Which pre/post hooks are active and what they enforce
> - **Cost Guardrails**: Adjust the $15/hr cap if needed for this project
> - **Stack Reference**: Update with project-specific tools, frameworks, and conventions

### 2.2 — Customize Statusline

> Update the statusline to match the DDD we just outlined using the ADRs and available hooks and helpers.
>
> The statusline should reflect:
> - Current bounded context being worked on
> - Swarm status (agents active, topology)
> - Memory tier usage (Beads count, AgentDB patterns)
> - Active hooks (pre/post edit, security, quality)
> - Cost tracking against our project budget
> - Any active worktrees

### 2.3 — Pretrain Ruflo on the Plan

```bash
hooks-train            # Deep pretrain with the new CLAUDE.md and ADRs
gnx-analyze            # Rebuild graph with ADR/DDD docs included
neural-train           # Train neural patterns on the project structure
aqe-generate           # Validate the customized environment
aqe-gate               # QE gate — environment must be consistent before execution
bd add --type decision "Environment customized for [project name] — QE passed"
```

---

## Phase 3: Execute (Swarm Implement)

### 3.1 — Full Implementation

This is the execution prompt. It does everything.

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
> - No agent crosses bounded context boundaries without going through the Teammate plugin
>
> **Anti-Corruption Layer**: When contexts need to communicate, define explicit interfaces. No agent reads another agent's internal models directly.
>
> **QE Gate (mandatory after each bounded context completes):**
> - Run the full Agentic QE pipeline: `aqe-generate` then `aqe-gate`
> - QE must verify: test coverage, security scan, code quality, pattern consistency, missing edge cases
> - If QE identifies gaps, fix them before moving to the next context
> - After ALL contexts complete, run QE one final time across the entire codebase
> - Do not stop until all contexts are implemented, tested, QE-verified, and passing quality gates

### 3.2 — Incremental Implementation (One Context at a Time)

If you prefer controlled rollout:

> Implement the [context name] bounded context only. Follow the ADR/DDD plan.
>
> 1. `wt-add [context-name]` — isolate the work
> 2. Implement all domain logic, services, interfaces
> 3. Use UI UX Pro Max for any UI components in this context
> 4. Security scan
> 5. Performance profile
> 6. **Run full Agentic QE pipeline**: `aqe-generate` then `aqe-gate` — fix any gaps before proceeding
> 7. Document
> 8. Merge to main
> 9. `wt-remove [context-name]`
> 10. `gnx-analyze` — update graph
> 11. `bd add --type decision "[context-name] implemented and merged — QE passed"`
>
> Do NOT move to the next context until QE passes on this one.

### 3.3 — Parallel Implementation

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
>
> **QE Gate per agent**: Each agent runs `aqe-generate` + `aqe-gate` on its context before marking complete. Fix gaps before merge.
>
> When all complete:
> 1. Merge in the order specified in the plan
> 2. `aqe-gate` after each merge — must pass before next merge
> 3. `gnx-analyze` after each merge
> 4. **Final full QE pipeline across entire codebase**: `aqe-generate` + `aqe-gate`
> 5. `wt-clean`
> 6. `bd add --type decision "Parallel implementation complete — QE passed all contexts"`

---

## Phase 4: Continue / Iterate

### 4.1 — Resume Work

> `bd-ready` shows [describe what Beads reports]. Continue implementation from where we left off.
>
> Check the knowledge graph (`gnx-status`) and pick up the next bounded context from the plan. Follow the same protocol: worktree, implement, test, gate, merge, record.

### 4.2 — Add a Feature

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
> 2. Implement
> 3. **Run full Agentic QE pipeline**: `aqe-generate` + `aqe-gate` — fix any gaps before merge
> 4. Merge, `wt-remove`, `gnx-analyze`
> 5. `bd add --type issue "Feature [name] shipped — QE passed"`

### 4.3 — Refactor

> Refactor [module] to [goal].
>
> Safety protocol:
> 1. `gnx-analyze` — current graph
> 2. GitNexus blast radius — what depends on this module?
> 3. Generate characterization tests first: `aqe-generate`
> 4. `wt-add refactor-[name]`
> 5. Refactor in isolation
> 6. All characterization tests must still pass
> 7. **Run full Agentic QE pipeline**: `aqe-generate` + `aqe-gate` — verify no regressions, no gaps introduced
> 8. Merge, cleanup
> 9. `gnx-analyze`
> 10. `bd add --type decision "Refactored [module]: [why and what changed] — QE passed"`

---

## Phase 5: Troubleshooting

### 5.1 — Bug Fix

> Bug: [describe].
>
> 1. `bd-ready` — any known issues here?
> 2. GitNexus: trace the execution path from [trigger] through the dependency graph
> 3. `wt-add bugfix-[name]`
> 4. Write failing test → fix → test passes
> 5. **Run full Agentic QE pipeline**: `aqe-generate` + `aqe-gate` — verify no regressions, no new gaps
> 6. Merge, cleanup, `gnx-analyze`
> 7. `bd add --type issue "Fixed: [description] — QE passed"`

### 5.2 — Production Incident

> Incident: [symptoms].
>
> 1. `bd-ready` — recent changes?
> 2. GitNexus: trace affected path
> 3. Perf Optimizer: profile the affected endpoint
> 4. `wt-add hotfix-[name]`
> 5. Minimal fix (Ruflo routes to Opus for critical reasoning)
> 6. **Run Agentic QE pipeline**: `aqe-generate` + `aqe-gate` — must pass before merge
> 7. Merge hotfix immediately
> 8. `bd add --type issue "INCIDENT: [root cause] — [fix] — QE passed"`
> 9. Create follow-up ADR if needed, run QE on the ADR

### 5.3 — Dependency Update

> Update [package] from [old] to [new].
>
> 1. `gnx-analyze` — rebuild graph
> 2. GitNexus: what imports from this package? Full blast radius.
> 3. Code Intelligence: find deprecated API usage
> 4. `wt-add dep-update`
> 5. Update all affected files
> 6. **Run full Agentic QE pipeline**: `aqe-generate` + `aqe-gate` — verify all affected modules still work
> 6. `aqe-generate` + `aqe-gate`
> 7. Merge, cleanup, `gnx-analyze`
> 8. `bd add --type decision "Updated [package] [old] → [new]"`

---

## Phase 6: GitOps & Release

### 6.1 — Release

> Prepare release v[X.Y.Z].
>
> 1. `bd-ready` — review all decisions/issues since last release
> 2. **Run full Agentic QE pipeline across entire codebase**: `aqe-generate` + `aqe-gate` — no release without QE pass
> 3. Security scan
> 4. Generate changelog from `bd-list`
> 5. `git tag -a v[X.Y.Z] -m "Release [X.Y.Z]"`
> 6. `bd add --type decision "Released v[X.Y.Z] — QE passed"`

### 6.2 — Branch Strategy with Worktrees

```bash
# Feature work
wt-add feature-[name]
# ... implement, test, gate ...
# merge to main
wt-remove feature-[name]

# Hotfix
wt-add hotfix-[name]
# ... fix, gate ...
# merge to main
wt-remove hotfix-[name]

# Always after merge
gnx-analyze
bd add --type decision "[what was merged]"
```

---

## Phase 7: Knowledge & Handoff

### 7.1 — End of Session

```bash
bd add --type issue "[unfinished work]"
bd add --type decision "[decisions made]"
bd add --type issue "[blockers found]"
gnx-analyze
neural-patterns        # What did Ruflo learn?
```

### 7.2 — Onboarding a New Codebase

```bash
gnx-analyze            # Build knowledge graph
gnx-wiki               # Generate wiki
gnx-serve              # Visual explorer
hooks-train            # Pretrain on the codebase
bd init                # Initialize memory
```

Then:

> Analyze this codebase using GitNexus and the Code Intelligence plugin. Identify: architecture patterns, bounded contexts, technical debt, security concerns, test coverage gaps. Record findings in Beads.

### 7.3 — Health Check

```bash
rf-doctor
turbo-status
gnx-analyze
aqe-gate
neural-patterns
mem-stats
bd-ready
```

> Run the Perf Optimizer on critical paths. Use Code Intelligence to find anti-patterns. Use Test Intelligence to identify coverage gaps. Record all findings in Beads.

---

## CLAUDE.md Customization Template

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
- Project decisions → `bd add --type decision`
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

## Quick Reference

| What you want to do | Prompt / Command |
|---------------------|-----------------|
| Start a session | `bd-ready && gnx-status && turbo-status` |
| Plan from research | "Review `/plans/research` and create detailed ADR/DDD... do not implement yet" |
| Customize environment | "Update CLAUDE.md to match the DDD" + "Update statusline" |
| Implement everything | "Spawn swarm, implement completely, test, validate, benchmark, optimize, document, continue until complete" |
| Implement one context | "Implement [context] only" + `wt-add` + `aqe-gate` |
| Implement in parallel | `wt-add` × N + `rf-swarm` |
| Add a feature | `bd-ready` + blast radius + `wt-add` + implement + `aqe-gate` |
| Refactor | characterization tests + `wt-add` + refactor + tests pass + `aqe-gate` |
| Fix a bug | `wt-add` + failing test + fix + `aqe-gate` |
| Hotfix production | `wt-add` + minimal fix + `aqe-gate` + merge immediately |
| Update dependency | GitNexus blast radius + `wt-add` + update + `aqe-gate` |
| Release | `bd-list` for changelog + `aqe-gate` + `git tag` |
| End session | `bd add` (issues + decisions) + `gnx-analyze` |
| Onboard new codebase | `gnx-analyze` + `gnx-wiki` + `hooks-train` + `bd init` |
