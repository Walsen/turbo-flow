# CLAUDE.md — TurboFlow 4.0 / Ruflo v3.5

## Identity
TurboFlow 4.0 — composed agentic development environment.
Orchestration: Ruflo v3.5 (259 MCP tools · 60+ agents · 8 AgentDB controllers · 17 hooks · 12 workers).
Memory: Five-tier (Context Autopilot → Beads → Ruflo Memory/HNSW → AgentDB → Native Tasks).
Isolation: Git worktrees per parallel agent.

---

## BEHAVIORAL RULES (always enforced)

- Do what has been asked; nothing more, nothing less
- NEVER create files unless absolutely necessary — prefer editing existing files
- NEVER proactively create .md or README files unless explicitly requested
- NEVER save working files or tests to the root folder
- ALWAYS read a file before editing it
- NEVER commit secrets, credentials, or .env files
- Never continuously check status after spawning a swarm — wait for results
- **NEVER merge to `main` without the Triple-Gate Merge Protocol**
- **NEVER force-push to `main` under any circumstances**
- **NEVER bypass or batch the 3-confirmation merge sequence — each gate is a separate turn**
- ALWAYS end action responses with the Status HUD
- NEVER run destructive commands without confirmation (see DESTRUCTIVE COMMAND SAFEGUARDS)
- ALWAYS run tests before committing (if a test suite exists)
- After 3 failed approaches to the same problem — STOP and ask the human
- ALWAYS clean up worktrees after merge — `wt-clean` is mandatory
- ALWAYS use non-interactive shell flags — `cp -f`, `mv -f`, `rm -f` — aliased `-i` hangs agents
- ALWAYS use `--json` flag with `bd` commands

---

## STATUS HUD (always enforced)

After every action response (file edit, bash, task completion, git op), end with:

```
───────────────────────────────────
📍 Branch: feat/user-system · 3 files changed
🧠 Memory: Beads ✅ · Ruflo HNSW ✅ · AgentDB ✅ · Context Autopilot ✅
🔧 Daemon: running · workers: map ✅ audit ✅ optimize ⏸
🌿 Worktrees: 2 active (if any)
🤖 Agents: 2/4 active (if spawned)
🧪 Tests: passing (42/42) · last run: 3m ago
💰 Session cost: $2.34 · budget remaining: $12.66/hr
⚡ Model: Sonnet 4.5 (routed — confidence 0.87)
───────────────────────────────────
```

Show only active systems — omit lines for inactive ones. Always show Branch + Memory + Daemon. Show 🧪 if tests exist. Show ⚠️ for unresolved pre-flight warnings. Do NOT show after pure conversation. On task completion add `✅ Completed:` summary above HUD. On errors surface `⚠️` at TOP, auto-fix, proceed. On boot show full system status table with 🟢/🟡/🔴 overall.

---

## TRIPLE-GATE MERGE PROTOCOL (zero exceptions)

Any merge/rebase/push into `main` (`master`/`production`/`prod`/`release`) = 3 consecutive human confirmations. No agent may merge autonomously.

```
GATE 1 — "🔒 MERGE GATE 1/3: Merging [branch] → main. [changes, commits, risk]. Confirm?"
GATE 2 — "🔒 MERGE GATE 2/3: Tests: [pass/fail]. Conflicts: [y/n]. Uncommitted: [y/n]. Confirm?"
GATE 3 — "🔒 MERGE GATE 3/3: FINAL. Type 'yes' to execute."
```

Each gate = separate turn. Non-`yes` = abort. Run `gitnexus_detect_changes` between gates 1–2. Sub-agents escalate to lead. Hotfixes not exempt. Does NOT apply to: feature-to-feature merges, non-primary branch pushes, commits, branch/tag/worktree creation.

---

## DESTRUCTIVE COMMAND SAFEGUARDS

One confirmation before: `git reset --hard`, `rm -rf` (project dirs), `prisma migrate reset`, `DROP TABLE`, any `--force` that deletes data. Format: `⚠️ DESTRUCTIVE: [command]. [consequence]. Confirm?`

## ROLLBACK PROTOCOL

Main breaks → `git revert --no-commit HEAD` → test → commit → push (skips Triple-Gate) → tell human → `bd create "[branch] reverted" -t bug -p 0 --json` → `ruv-remember "revert/[branch]" "cause"`

## CONFLICT RESOLUTION

Never silently auto-resolve. Simple (non-overlapping): resolve + show. Complex (overlapping logic): show both sides, ask human. Always test + `gitnexus_detect_changes` after.

---

## THE PRIME DIRECTIVE

**Human describes outcomes. You generate tasks. You execute. They review.**
Don't ask what to do. Boot memory → read codebase → TodoWrite → confirm plan → execute → report.

---

## MODEL ROUTING

Check hooks for `[AGENT_BOOSTER_AVAILABLE]` (Edit tool, $0) and `[TASK_MODEL_RECOMMENDATION]`.

| Tier | Handler | When |
|------|---------|------|
| 1 | Agent Booster (WASM) | Simple transforms — skip LLM |
| 2 | Haiku 4.5 | Formatting, quick lookups |
| 3 | Sonnet 4.5 / Opus 4.6 | Standard coding / complex reasoning |

Hard cap: $15/hr. Use Haiku for simple tasks.

---

## SESSION BOOT PROTOCOL (every session)

```bash
# 0. PRE-FLIGHT
git stash list && git status --short
test -f .env || test -f .env.local || echo "⚠️  NO .env"
npx prisma migrate status 2>/dev/null || echo "⚠️  Migrations pending"
df -h . | awk 'NR==2{if($5+0 > 90) print "⚠️  DISK " $5 " FULL"}'

# 1. DAEMON
npx ruflo@latest daemon start && npx ruflo@latest daemon status

# 2. HOOKS — verify registration + fire session start
cat .claude/settings.json | grep -c "hook" || echo "⚠️  NO HOOKS — run: npx ruflo@latest init"
npx ruflo@latest hooks session-start --session-id ${PROJECT_ID}

# 3. BEADS
bd ready --json && bd list --type blocker

# 4. INTELLIGENCE — if 0 patterns: npx ruflo@latest hooks pretrain --depth deep
npx ruflo@latest hooks intelligence stats

# 5. MEMORY — verify health then recall
npx ruflo@latest memory stats
npx ruflo@latest memory search -q "${PROJECT_ID} current state" --limit 5

# 6. AGENTDB — probe: agentdb_pattern-search({ query: "health check", limit: 1 })
#    If { available: false }: npm install -g @claude-flow/memory && npx ruflo@latest doctor --fix

# 7. GITNEXUS — auto-reindex if stale
npx gitnexus status
# If stale: npx gitnexus analyze --embeddings (or without if none exist)

# 8. SWARM
npx ruflo@latest swarm init --topology star --max-agents 4 --strategy solo_developer

# 9. SECURITY
npx ruflo@latest hooks worker list | grep -q "audit" || echo "⚠️  AUDIT WORKER NOT RUNNING"

# 10. ROUTE
npx ruflo@latest hooks route "${PROJECT_ID} session goals" --include-explanation
```

After boot: output full status table reflecting actual command output.

---

## SESSION END PROTOCOL

**Work is NOT complete until `git push` succeeds. NEVER say "ready to push when you are" — YOU push.**

```bash
# 1. File remaining work + close completed
bd create "Remaining" --description="Details" -t task -p 2 --json
bd close <id> --reason "Done" --json

# 2. Quality gates
npm test && npm run lint && npm run build

# 3. Persist learning
npx ruflo@latest hooks session-end --export-metrics true --persist-patterns true
npx ruflo@latest memory store --namespace ${PROJECT_ID} --key "session/$(date +%Y-%m-%d)" --value "completed: [X], next: [Z]"

# 4. Sync + push (MANDATORY)
bd dolt push
git add -A && git commit -m "chore: session end" 2>/dev/null
git pull --rebase && git push
git status  # MUST show "up to date with origin"

# 5. Daemon checkpoint
npx ruflo@latest daemon trigger audit
```

---

## MEMORY SYSTEM

### Layer 1: Context Autopilot (automatic)
`UserPromptSubmit` archives to SQLite. `PreCompact` blocks compaction. `SessionStart` restores. If broken: `npx ruflo@latest doctor --fix`

### Layer 2: Beads (bd) — Project Truth
Git-native JSONL. ALL issue tracking — no markdown TODOs.

```bash
bd ready --json                                    # unblocked work
bd create "Title" --description="Details" -t bug|feature|task|epic|chore -p 0-4 --json
bd create "Title" -p 2 --deps discovered-from:<id> --json
bd update <id> --claim --json
bd close <id> --reason "Done" --json
bd defer <id> | bd supersede <id> | bd human <id>
bd stale | bd orphans | bd lint                    # hygiene
bd prime                                           # full workflow context
bd remember "key" "value"                          # persistent knowledge
bd dolt push | bd dolt pull
```

Types: `bug`·`feature`·`task`·`epic`·`chore`. Priorities: `0` critical → `4` backlog.

### Layer 3: Ruflo Memory — HNSW
```bash
npx ruflo@latest memory store --namespace ${PROJECT_ID} --key "area/fix" --value "solution"
npx ruflo@latest memory search -q "keywords" --limit 5
# Aliases: ruv-remember | ruv-recall | mem-search | mem-stats
```

### Layer 4: AgentDB v3 — MCP Tools
`agentdb_pattern-search` (USE BEFORE solving bugs) · `agentdb_pattern-store` · `agentdb_context-synthesize` · `agentdb_semantic-route` · `agentdb_hierarchical-store/recall`

### Layer 5: Native Tasks (TodoWrite)
Batch ALL todos in ONE call (5–10+ min). Never call TodoWrite multiple times per session.

---

## PARALLEL EXECUTION

**Pattern A — Swarm:** Init → spawn ALL agents in ONE message → ONE TodoWrite → store state. Always concurrent.

**Pattern B — Worktrees:** `git worktree add .worktrees/feat-a -b feat/feat-a`. Test before merging. Triple-Gate for main. `wt-clean` after.

**Pattern C — Headless:** `claude -p "task" &` | `--model haiku` | `--max-budget-usd 0.50` | `--resume "id" --fork-session`

---

## ISOLATION RULES

One worktree per agent. PG Vector isolation via `$DATABASE_SCHEMA`. No `--dangerously-skip-permissions` on bare metal. Always `gitnexus_impact` before shared symbols. Always `gitnexus_detect_changes` before commits.

## AGENT TEAMS

`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` enabled. Lead → up to 3 teammates (depth 2). 3+ blocked → alert human. Create tasks before spawning. `run_in_background: true`. Sub-agents cannot merge to main — escalate to lead.

## HIVE-MIND

```bash
npx ruflo@latest hive-mind init --topology hierarchical-mesh --consensus raft --name ${PROJECT_ID}-sprint
npx ruflo@latest hive-mind spawn --agents 4 --strategy specialized
npx ruflo@latest hive-mind resume --name ${PROJECT_ID}-sprint
```

---

## HOOKS (automatic)

`UserPromptSubmit` (archive) · `PreToolUse:Write/Edit` (verify) · `PostToolUse:Write/Edit` (record) · `PreCompact` (block) · `SessionStart` (restore) · `SessionEnd` (persist) · `TeammateIdle` (auto-assign) · `TaskCompleted` (train)

Key manual: `hooks session-start|end|restore` · `hooks route` · `hooks post-task` · `hooks pretrain --depth deep` · `hooks intelligence stats` · `hooks worker list|dispatch`

---

## GOAL-TO-TASK PROTOCOL

1. Boot (skip if booted) → 2. Route goal → 3. Recall: `memory search` + `agentdb_pattern-search` → 4. Read files + `gitnexus_impact` → 5. ONE TodoWrite (5–10+) → 6. Present plan, wait for confirm → 7. Execute parallel → 8. Test → 9. `post-task` + `ruv-remember` → 10. Session end

---

## SECURITY

`npx ruflo@latest security scan --depth full` · `security audit|cve|threats|validate|report`

Pre-edit hooks enforce: no secrets, no mocks in prod, HTTPS, validated inputs.

## HEALTH

`npx ruflo@latest doctor --fix` · `turbo-status` · `rf-doctor`

---

## PROJECT CONTEXT
<!-- Fill in per project. Everything above is universal. -->

```
PROJECT_ID=your-project-name
```

Fill in below: tech stack, required env vars (no values), known issues, architecture decisions.

---

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do
- **MUST** `gitnexus_impact({target: "symbolName", direction: "upstream"})` before editing any symbol.
- **MUST** `gitnexus_detect_changes()` before committing.
- **MUST warn user** on HIGH/CRITICAL risk.
- Use `gitnexus_query` instead of grep. Use `gitnexus_context` for full symbol view.

## When Debugging
1. `gitnexus_query({query: "<symptom>"})` 2. `gitnexus_context({name: "<suspect>"})` 3. `READ gitnexus://repo/${PROJECT_ID}/process/{name}` 4. Regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})`

## When Refactoring
- Rename: `gitnexus_rename({..., dry_run: true})` first. Extract: `context` + `impact` first. After: `detect_changes({scope: "all"})`.

## Never Do
- NEVER edit without `gitnexus_impact`. NEVER ignore HIGH/CRITICAL. NEVER find-and-replace — use `gitnexus_rename`. NEVER commit without `detect_changes`.

## Tools
| Tool | Command |
|------|---------|
| `query` | `gitnexus_query({query: "..."})` |
| `context` | `gitnexus_context({name: "..."})` |
| `impact` | `gitnexus_impact({target: "...", direction: "upstream"})` |
| `detect_changes` | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | `gitnexus_cypher({query: "MATCH ..."})` |

## Risk: d=1 WILL BREAK (must update) · d=2 LIKELY AFFECTED (test) · d=3 MAY NEED TESTING

## Resources
`gitnexus://repo/${PROJECT_ID}/context` · `clusters` · `processes` · `process/{name}`

## Pre-Finish Check
1. `impact` run for all modified symbols 2. No HIGH/CRITICAL ignored 3. `detect_changes` confirms scope 4. All d=1 dependents updated

## Index: `npx gitnexus analyze` (add `--embeddings` to preserve them). PostToolUse hook auto-updates after commit/merge.

## Skills
`.claude/skills/gitnexus/gitnexus-exploring|impact-analysis|debugging|refactoring|guide|cli/SKILL.md`

<!-- gitnexus:end -->
