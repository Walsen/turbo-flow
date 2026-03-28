# CLAUDE.md — TurboFlow 4.0 / Ruflo v3.5

## Identity
This workspace runs TurboFlow 4.0 — a composed agentic development environment.
Orchestration: Ruflo v3.5 (skills-based, not slash commands).
Memory: Five-tier (Context Autopilot → Beads → Ruflo Memory/HNSW → AgentDB → Native Tasks).
Isolation: Git worktrees per parallel agent.

> Ruflo v3.5 — stable release. 259 MCP tools · 60+ agents · 8 AgentDB controllers · 17 hooks · 12 workers.

---

## BEHAVIORAL RULES (always enforced)

- Do what has been asked; nothing more, nothing less
- NEVER create files unless absolutely necessary for achieving the goal
- ALWAYS prefer editing an existing file to creating a new one
- NEVER proactively create .md or README files unless explicitly requested
- NEVER save working files or tests to the root folder
- ALWAYS read a file before editing it
- NEVER commit secrets, credentials, or .env files
- Never continuously check status after spawning a swarm — wait for results
- **NEVER merge to `main` without completing the Triple-Gate Merge Protocol (see below)**
- **NEVER force-push to `main` under any circumstances**
- **NEVER bypass, batch, or shortcut the 3-confirmation sequence — each confirmation is a separate prompt/response cycle**
- ALWAYS end action responses with the Status HUD — the human should never have to ask what's running
- NEVER run destructive commands without confirmation — see DESTRUCTIVE COMMAND SAFEGUARDS below
- ALWAYS run tests before committing (if a test suite exists) — a commit with failing tests is a broken commit
- If you have attempted 3 different approaches to the same problem and all failed — STOP, explain what you tried, and ask the human how to proceed. Do not burn tokens on attempt #4+
- ALWAYS clean up worktrees after their branch is merged — `wt-clean` is not optional, it's part of the merge

---

## RESPONSE FORMAT — STATUS HUD (always enforced)

Every response that involves code changes, task execution, or system interaction MUST end with a compact status block. This is not optional. The human should never have to ask "what's running?" — it's always visible.

### After Every Code/Task Response

```
───────────────────────────────────
📍 Branch: feat/user-system · 3 files changed
🧠 Memory: Beads ✅ · Ruflo HNSW ✅ · AgentDB ✅ · Context Autopilot ✅
🔧 Daemon: running · workers: map ✅ audit ✅ optimize ⏸
🌿 Worktrees: 2 active (.worktrees/fix-auth, .worktrees/feat-billing)
🤖 Agents: 2/4 active (Coder-1: feat-billing, Tester: idle)
📊 Hooks: 14 fired this session · last: PostToolUse:Edit
🧪 Tests: passing (42/42) · last run: 3m ago
💰 Session cost: $2.34 · budget remaining: $12.66/hr
⚡ Model: Sonnet 4.5 (routed by QLearning — confidence 0.87)
───────────────────────────────────
```

### Rules

- Show only what's **actually active** — if no worktrees exist, omit that line. If no agents are spawned, omit that line. Don't show blank/N/A lines.
- Always show: Branch, Memory status, Daemon status (or "not running" if it isn't)
- Show 🧪 Tests line if a test suite exists — show last result and time since run. If tests are failing, always show this line even if other optional lines are omitted.
- If pre-flight found warnings (missing .env, pending migrations, stashes), keep showing those as ⚠️ lines until resolved
- Show after: any file edit, any bash command, any task completion, any agent spawn/completion, any git operation
- Do NOT show after: pure conversation, answering questions, explaining concepts — only after action
- Keep it to **one line per system** — no paragraphs, no explanations in the HUD
- Use the emoji prefix exactly as shown — it makes scanning fast

### On Session Boot

After the boot protocol completes, show a full system status instead of the compact HUD:

```
╔══════════════════════════════════════════════════════╗
║              ⚡ TURBOFLOW SESSION LIVE ⚡              ║
╠══════════════════════════════════════════════════════╣
║  Project:    ${PROJECT_ID}                           ║
║  Branch:     current-branch                          ║
║  Stack:      Next.js / Prisma / TypeScript           ║
╠──────────────────────────────────────────────────────╣
║  SYSTEM             STATUS                           ║
╠──────────────────────────────────────────────────────╣
║  Daemon              ✅ running (3 workers)          ║
║  Hooks               ✅ 17 registered                ║
║  Context Autopilot   ✅ archiving (42 turns stored)  ║
║  Beads               ✅ 8 open issues · 2 blockers   ║
║  Ruflo Memory        ✅ 156 entries · HNSW indexed   ║
║  AgentDB             ✅ 8 controllers online         ║
║  GitNexus            ✅ fresh (last: 2m ago)         ║
║  Intelligence        ✅ 340 patterns · Q-table warm  ║
║  Swarm               ✅ star topology · 4 max        ║
║  Agent Teams         ⏸ not spawned                   ║
║  Hive-Mind           ⏸ not initialized               ║
║  Security            ✅ pre-edit hooks active         ║
╠──────────────────────────────────────────────────────╣
║  PRE-FLIGHT                                          ║
╠──────────────────────────────────────────────────────╣
║  .env file           ✅ found | ⚠️  missing           ║
║  DB migrations       ✅ current | ⚠️  pending         ║
║  Stashed work        ✅ none | ⚠️  N stashes found    ║
║  Uncommitted files   ✅ clean | ⚠️  N files dirty     ║
║  Disk space          ✅ healthy | ⚠️  >90% full       ║
╠──────────────────────────────────────────────────────╣
║  Blockers: #12 (db migration pending)                ║
║  Last session: completed RBAC UI, learned: ...       ║
║  Routed goal: [from hooks route output]              ║
╠──────────────────────────────────────────────────────╣
║  🟢 ALL SYSTEMS GO                                   ║
╚══════════════════════════════════════════════════════╝
```

### On Task Completion

When finishing a task (not just a single edit — a full unit of work), add a one-line summary above the HUD:

```
✅ Completed: Implemented AI call tracking — 4 files changed, 2 tests added, quota now enforced
───────────────────────────────────
📍 Branch: feat/ai-tracking · +142 -23 lines
🧠 Memory: all layers active · stored pattern "ai-quota-enforcement"
...
───────────────────────────────────
```

### On Errors or Degraded State

If any system is down or a command fails, call it out at the TOP of the response, not buried in output:

```
⚠️  GitNexus index stale (last analyzed 4h ago) — running `npx gitnexus analyze`
⚠️  AgentDB returned { available: false } — running `npx ruflo@latest doctor --fix`
```

Then proceed with the work. Don't stop to ask — fix it and report.

---

## TRIPLE-GATE MERGE PROTOCOL (MANDATORY — zero exceptions)

Any operation that merges, rebases, fast-forwards, or pushes commits into `main` (or the project's primary production branch) MUST pass three consecutive human confirmations. This includes `git merge`, `git rebase onto main`, `git push origin main`, PR merge commands, and any MCP tool or script that results in main being updated.

**No agent, sub-agent, teammate, swarm worker, or background task may merge to main autonomously. Ever.**

### Gate Sequence

```
GATE 1 — INTENT
  Agent: "🔒 MERGE GATE 1/3: I am about to merge [branch] into main.
          Changes: [summary — files changed, lines added/removed]
          Commits: [count and last 3 commit messages]
          Risk: [gitnexus impact summary if available]
          Confirm? (yes/no)"
  Human: "yes"

GATE 2 — VERIFICATION
  Agent: "🔒 MERGE GATE 2/3: Confirming merge of [branch] → main.
          Tests passing: [yes/no/not run]
          Uncommitted changes: [yes/no]
          Conflicts detected: [yes/no]
          This is irreversible on remote. Confirm again? (yes/no)"
  Human: "yes"

GATE 3 — FINAL AUTHORIZATION
  Agent: "🔒 MERGE GATE 3/3: FINAL confirmation.
          Merging [branch] → main and pushing to origin.
          Type 'yes' to execute."
  Human: "yes"
```

### Rules

- Each gate MUST be a **separate prompt/response turn** — all three cannot appear in a single message
- If the human responds with anything other than exactly `yes` (case-insensitive) at any gate, the merge is **aborted immediately** and the agent reports "Merge aborted at Gate N"
- If the human says `yes` then later says `no` or `stop` or `wait` — abort and do not re-enter the sequence without starting over from Gate 1
- The agent MUST run `gitnexus_detect_changes` (if available) between Gate 1 and Gate 2 and include the output in Gate 2
- Sub-agents and swarm workers that need to merge to main MUST escalate to the lead agent, who then runs the Triple-Gate with the human — workers cannot run gates themselves
- This protocol applies to **all synonyms**: `main`, `master`, `production`, `prod`, `release`, or whatever the project's primary branch is named
- Hotfixes are NOT exempt — they go through all three gates

### What Does NOT Require Triple-Gate

- Merging between feature branches (e.g., `feat/a` → `feat/b`)
- Pushing to any non-primary branch
- Creating branches, tags, or worktrees
- `git commit` on any branch (including main — committing is fine, pushing/merging is gated)

---

## DESTRUCTIVE COMMAND SAFEGUARDS

These commands require **one explicit human confirmation** before execution, on ANY branch:

```
git reset --hard          git clean -fd             rm -rf (on project dirs)
prisma migrate reset      prisma db push --force    DROP TABLE / DROP DATABASE
npm cache clean --force   docker system prune       Any command with --force that deletes data
```

Format: `⚠️ DESTRUCTIVE: About to run [command]. This will [consequence]. Confirm? (yes/no)`

One confirmation is enough — this is not Triple-Gate. The point is to prevent accidental data loss, not to slow you down.

**No confirmation needed for:** `rm` on temp/generated files, `git clean` on build artifacts, `prisma migrate dev` (non-destructive), `docker stop`.

---

## ROLLBACK PROTOCOL — WHEN MAIN BREAKS

If a merge to main causes failures (tests break, app won't start, production errors):

```
1. IMMEDIATELY: git revert --no-commit HEAD    (undo the merge, don't auto-commit)
2. VERIFY:      run tests / start app           (confirm revert fixes it)
3. COMMIT:      git commit -m "revert: [branch] merge — [reason]"
4. PUSH:        git push origin main            (no Triple-Gate needed for emergency reverts)
5. REPORT:      tell the human what broke and why
6. BEAD:        bd add --type blocker "[branch] merge reverted — [reason]"
7. STORE:       ruv-remember "revert/[branch]" "what went wrong and root cause"
```

Emergency reverts to main do NOT require Triple-Gate — speed matters when production is broken. Log everything so the fix attempt has context.

---

## CONFLICT RESOLUTION

When `git merge` produces conflicts:

- **NEVER auto-resolve conflicts silently.** Show the human which files conflict and what each side changed.
- **For simple conflicts** (non-overlapping changes in same file): resolve, show the resolution, continue.
- **For complex conflicts** (overlapping logic, competing implementations): show both sides and ask the human which approach to keep.
- **After resolution**: run tests before committing the merge.
- **Always run** `gitnexus_detect_changes` after conflict resolution to verify scope.

---

## THE PRIME DIRECTIVE

**The human describes outcomes. You generate tasks. You execute them. They review.**

When given a goal — do NOT ask what to do. Boot memory, read the codebase, generate a full TodoWrite, confirm with the human, execute in parallel, report back.

---

## 3-TIER MODEL ROUTING — CHECK THIS FIRST

Before any LLM call, check hook output for routing signals:

```
[AGENT_BOOSTER_AVAILABLE]    → Use Edit tool directly. $0. <1ms. No LLM needed.
  Intent types: var-to-const, add-types, add-error-handling,
                async-await, add-logging, remove-console

[TASK_MODEL_RECOMMENDATION]  → Use specified model in Task tool.
```

| Tier | Handler | Latency | Cost | When |
|------|---------|---------|------|------|
| 1 | Agent Booster (WASM) | <1ms | $0 | Simple transforms — skip LLM entirely |
| 2 | Haiku 4.5 | ~500ms | low | Simple tasks, formatting, quick lookups |
| 3 | Sonnet 4.5 | ~1s | medium | Standard coding, implementation |
| 3 | Opus 4.6 | 2–5s | higher | Architecture decisions, complex reasoning |

Hard cap: $15/hr. Always use hierarchical topology for coding swarms. Use Haiku for simple tasks — don't burn Opus on formatting.

---

## SESSION BOOT PROTOCOL (MANDATORY — every session)

```bash
# 0. PRE-FLIGHT — catch problems before they cascade
git stash list                                          # surface any forgotten stashed work
git status --short                                      # uncommitted changes from last session?
test -f .env || test -f .env.local || echo "⚠️  NO .env FILE FOUND"
npx prisma migrate status 2>/dev/null || echo "⚠️  Prisma not available or migrations pending"
df -h . | awk 'NR==2{if($5+0 > 90) print "⚠️  DISK " $5 " FULL"}'

# 1. DAEMON — start background workers
npx ruflo@latest daemon start
npx ruflo@latest daemon status

# 2. HOOKS SESSION START — fires context restore, loads intelligence
npx ruflo@latest hooks session-start --session-id ${PROJECT_ID}

# 3. BEADS — project truth
bd ready
bd list --type blocker

# 4. INTELLIGENCE — what the system has learned
npx ruflo@latest hooks intelligence stats
node .claude/helpers/hook-handler.cjs stats

# 5. MEMORY — semantic recall (HNSW-indexed)
npx ruflo@latest memory search -q "${PROJECT_ID} current state" --limit 5
npx ruflo@latest memory search -q "${PROJECT_ID} blockers" --limit 3

# 6. GITNEXUS — codebase graph freshness
npx gitnexus status
# If stale: npx gitnexus analyze
# If embeddings exist: npx gitnexus analyze --embeddings

# 7. SWARM INIT — solo dev star topology (anti-drift)
npx ruflo@latest swarm init --topology star --max-agents 4 --strategy solo_developer

# 8. ROUTE TODAY'S WORK
npx ruflo@latest hooks route "${PROJECT_ID} session goals" --include-explanation
```

> Replace `${PROJECT_ID}` with your project name (e.g. `rentamls`, `myapp`). Set once in PROJECT CONTEXT below.

**Why this works:** Ruflo's `SessionStart` hook auto-fires `context-persistence-hook` which restores archived conversation turns from SQLite — context is never lost to compaction. The manual boot adds semantic memory recall and intelligence initialization on top.

**After boot completes:** Output the full TURBOFLOW SESSION LIVE status table (defined in Response Format section). Every system line must reflect actual output from the boot commands — do not guess or assume status.

---

## SESSION END PROTOCOL (MANDATORY — before closing)

```bash
# 1. Persist all learning
npx ruflo@latest hooks session-end --export-metrics true --persist-patterns true

# 2. Store session summary
npx ruflo@latest memory store \
  --namespace ${PROJECT_ID} \
  --key "session/$(date +%Y-%m-%d)" \
  --value "completed: [X], learned: [Y], next: [Z]"

# 3. Train on success (feeds the self-learning loop)
npx ruflo@latest hooks post-task \
  --task-id "${PROJECT_ID}-$(date +%Y%m%d)" \
  --success true \
  --store-results true

# 4. File beads
bd add --type decision "architectural choice made this session"
bd add --type issue "anything found but not fixed"
bd dolt push

# 5. Daemon checkpoint
npx ruflo@latest daemon trigger audit
```

---

## MEMORY SYSTEM — ALL FIVE LAYERS

### Layer 1: Context Autopilot (automatic)

Three hooks fire automatically to prevent context loss:

```
UserPromptSubmit → archives turns to SQLite (incremental)
PreCompact       → archives + BLOCKS auto-compaction (exit code 2) — context never lost
SessionStart     → restores from archive via additionalContext (importance-ranked)
```

These fire if hooks are registered in `.claude/settings.json` (done by `npx ruflo init`).
If context is still being lost: `npx ruflo@latest doctor --fix`

---

### Layer 2: Beads (bd) — Project Truth

Git-native JSONL. Persists in the repo. Source of truth for everything that matters across sessions.

```bash
# SESSION START — always run
bd ready                    # all open issues, blockers, decisions
bd ready --json             # machine-readable
bd list --type blocker
bd list --type decision
bd show <id>

# DURING SESSION — write constantly
bd add --type issue "description"
bd add --type blocker "what's blocking and why"
bd add --type decision "what was decided and why"
bd update <id> --claim      # claim before starting work
bd close <id>               # mark done when complete
bd dolt push                # sync to remote
```

What goes in Beads: every bug found (even unfixed), every architecture decision, every blocker, every completed feature. Anything you'd want to know at the start of the next session.

---

### Layer 3: Ruflo Memory — HNSW Semantic Search

SQLite-backed via `.swarm/memory.db`. Use `memory search` — it matches by vector similarity, not keyword. 150x–12,500x faster than naive scan.

```bash
# STORE patterns and solutions after every fix
npx ruflo@latest memory store \
  --namespace ${PROJECT_ID} \
  --key "area/what-was-fixed" \
  --value "description of the solution"

npx ruflo@latest memory store \
  --namespace ${PROJECT_ID} \
  --key "stack/env-vars" \
  --value "list of required env vars for this project"

npx ruflo@latest memory store \
  --namespace collaboration \
  --key "design-decisions" \
  --value "key architectural choices made"

# SEARCH — primary way to recall prior solutions
npx ruflo@latest memory search -q "relevant keywords" --limit 5

# RETRIEVE specific key
npx ruflo@latest memory retrieve --namespace ${PROJECT_ID} --key "area/what-was-fixed"

# STATS
npx ruflo@latest memory stats

# Aliases
ruv-remember "key" "value"
ruv-recall "query"
mem-search "query"
mem-stats
```

---

### Layer 4: AgentDB v3 — 8 Controllers (via MCP tools)

AgentDB is accessed via MCP tool names inside Task agents and swarm coordination — not as a direct CLI subcommand.

**Core Memory MCP tools:**
```
agentdb_hierarchical-store   → working → episodic → semantic memory tiers
agentdb_hierarchical-recall  → recall with Ebbinghaus forgetting curves
agentdb_consolidate          → cluster and merge related memories
agentdb_batch                → bulk insert/update/delete
```

**Intelligence MCP tools:**
```
agentdb_pattern-store        → store reusable pattern (BM25 + semantic hybrid search)
agentdb_pattern-search       → find prior solutions — USE THIS before solving any bug
agentdb_semantic-route       → route task to best agent by vector similarity
agentdb_context-synthesize   → auto-generate context summary from memory
agentdb_causal-edge          → recall with causal re-ranking
```

**Security (automatic, always-on):**
```
AttestationLog               → immutable audit trail
MutationGuard                → cryptographic proof on mutations
GuardedVectorBackend         → proof-of-work on vector ops
```

How to use inside a Task agent:
```
mcp__claude-flow__agentdb_pattern-store({ key: "${PROJECT_ID}/fix/area", value: "solution description", tags: ["${PROJECT_ID}"] })
mcp__claude-flow__agentdb_pattern-search({ query: "error description", limit: 5 })
mcp__claude-flow__agentdb_semantic-route({ task: "task description" })
mcp__claude-flow__agentdb_context-synthesize({ namespace: "${PROJECT_ID}", limit: 10 })
```

⚠️ If AgentDB tools return `{ available: false }`:
```bash
npm install -g @claude-flow/memory
npx ruflo@latest doctor --fix
```

---

### Layer 5: Native Tasks (TodoWrite)

Claude Code's built-in task system. **Always generated by the agent — never by the human.**

```
// ALWAYS batch ALL todos in ONE call (5–10+ minimum)
// NEVER call TodoWrite multiple times in a session
TodoWrite { todos: [
  { id: "1", content: "task description", status: "pending", priority: "high" },
  { id: "2", content: "task description", status: "pending", priority: "high" },
  { id: "3", content: "task description", status: "pending", priority: "medium" },
  { id: "4", content: "task description", status: "pending", priority: "low" }
]}
```

---

## PARALLEL EXECUTION — THREE PATTERNS

All operations MUST be concurrent in a single message. NEVER send related operations sequentially.

---

### Pattern A: MCP + Task Tool (standard swarm)

```
// STEP 1: Init swarm via MCP
mcp__ruv-swarm__swarm_init({ topology: "hierarchical", maxAgents: 8, strategy: "specialized" })

// STEP 2: Spawn ALL agents in ONE message
Task("Coordinator", "Initialize session. Run: npx ruflo@latest hooks session-start", "hierarchical-coordinator")
Task("Coder-1", "Work on feature A in .worktrees/feat-a", "coder")
Task("Coder-2", "Work on feature B in .worktrees/feat-b", "coder")
Task("Tester", "Write tests for both", "tester")

// STEP 3: ALL todos in ONE call
TodoWrite { todos: [...all tasks...] }

// STEP 4: Store swarm state
mcp__claude-flow__memory_usage({ action: "store", namespace: "swarm", key: "session", value: "..." })
```

---

### Pattern B: Git Worktrees (parallel independent file changes)

```bash
# Create isolated branches for independent work
git worktree add .worktrees/fix-area-a -b fix/area-a
git worktree add .worktrees/feat-area-b -b feat/area-b
# PG Vector isolation per worktree:
# Agent 1: DATABASE_SCHEMA=fix_area_a
# Agent 2: DATABASE_SCHEMA=feat_area_b

# After both agents complete — TRIPLE-GATE REQUIRED for each merge to main
git checkout main
# → Run tests on the feature branch BEFORE merging
# → Run Triple-Gate Merge Protocol for fix/area-a
git merge fix/area-a --no-ff
# → Run Triple-Gate Merge Protocol for feat/area-b
git merge feat/area-b --no-ff
git push origin main

# Cleanup — MANDATORY after merge, not optional
wt-clean
```

Branch naming convention:
- `fix/description` — bug fixes
- `feat/description` — new features
- `refactor/description` — refactoring
- `chore/description` — maintenance
- `pr-{number}` — PR review tasks (auto-created by GitHub Actions)

---

### Pattern C: Headless `claude -p` (background parallel tasks)

```bash
# Run tasks in parallel background
claude -p "task description A" &
claude -p "task description B" &
claude -p "task description C" &
wait    # wait for all

# With model selection
claude -p --model haiku "simple formatting task"
claude -p --model opus "complex architecture decision"

# With budget cap
claude -p --max-budget-usd 0.50 "bounded task"

# Resume and fork for exploring alternatives
claude -p --resume "session-id" "continue from last state"
claude -p --resume "session-id" --fork-session "try approach A"
claude -p --resume "session-id" --fork-session "try approach B"

# JSON output for scripting
claude -p --output-format json "structured task"
```

Key flags: `--model haiku/sonnet/opus`, `--max-budget-usd`, `--resume <id>`, `--fork-session`, `--fallback-model`, `--allowedTools`, `--output-format json`, `--dangerously-skip-permissions` (containers only).

---

## ISOLATION RULES

- Each parallel agent MUST operate in its own git worktree
- Create: `git worktree add .worktrees/agent-N -b agent-N/task-name`
- PG Vector isolation per worktree: use `$DATABASE_SCHEMA` env var
- NEVER run `--dangerously-skip-permissions` on bare metal — containers only
- ALWAYS run `gitnexus_impact` before editing any shared symbol
- ALWAYS run `gitnexus_detect_changes` before committing

---

## AGENT TEAMS

- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is enabled
- Lead agent may spawn up to 3 teammates
- Recursion limit: depth 2 (lead → sub-agents; sub-agents cannot spawn further)
- If 3+ agents blocked simultaneously → pause and alert the human
- Always create tasks before spawning (teammates need work to pick up)
- Always use `run_in_background: true` for parallel teammate execution
- Graceful shutdown: `SendMessage({ type: "shutdown_request", recipient: "name" })` before `TeamDelete`
- **Sub-agents and teammates CANNOT merge to main — they must escalate merge requests to the lead agent, who runs the Triple-Gate with the human**

```
// Standard Agent Teams pattern
TeamCreate({ team_name: "sprint-name" })

TaskCreate({ subject: "Task A", description: "detailed description" })
TaskCreate({ subject: "Task B", description: "detailed description" })

Task({ prompt: "Work on Task A. Check TaskList first.", subagent_type: "coder", team_name: "sprint-name", name: "agent-a", run_in_background: true })
Task({ prompt: "Work on Task B. Check TaskList first.", subagent_type: "coder", team_name: "sprint-name", name: "agent-b", run_in_background: true })

// Auto-assign when an agent finishes (fires automatically via hook, or manually)
npx ruflo@latest hooks teammate-idle --auto-assign true

// After task completion (fires automatically via hook, or manually)
npx ruflo@latest hooks task-completed --task-id "<id>" --train-patterns true
```

---

## HIVE-MIND — MULTI-SESSION PERSISTENT WORK

Use for sprints that span multiple days. Unlike swarm (dies on terminal close), Hive-Mind persists to SQLite and resumes exactly where it left off.

```bash
# Initialize once per sprint
npx ruflo@latest hive-mind init \
  --topology hierarchical-mesh \
  --consensus raft \
  --name ${PROJECT_ID}-sprint

npx ruflo@latest hive-mind spawn --agents 4 --strategy specialized

# Check status any time
npx ruflo@latest hive-mind status

# Resume after restarting terminal
npx ruflo@latest hive-mind resume --name ${PROJECT_ID}-sprint
```

Consensus strategies: `raft` (recommended, leader-based), `byzantine` (BFT, tolerates f < n/3 faulty), `gossip`, `crdt`, `quorum`.

---

## HOOKS SYSTEM

### Automatic (fire without you doing anything)
```
UserPromptSubmit       → archive turns, route via QLearningRouter
PreToolUse:Write/Edit  → pre-edit verification (no secrets, no mocks in prod, HTTPS)
PostToolUse:Write/Edit → record outcome, update Q-table
PostToolUse:Bash       → record bash outcomes
PreCompact             → archive + BLOCK compaction → context never lost
SessionStart           → restore from archive, load intelligence
SessionEnd             → persist patterns, update neural weights
Stop                   → final memory sync
SubagentEnd            → record outcome for routing improvement
TeammateIdle           → auto-assign pending tasks to idle teammates
TaskCompleted          → train patterns, notify lead
```

### Manual commands
```bash
# Session
npx ruflo@latest hooks session-start --session-id ${PROJECT_ID}
npx ruflo@latest hooks session-end --export-metrics true --persist-patterns true
npx ruflo@latest hooks session-restore --session-id ${PROJECT_ID}

# Task lifecycle
npx ruflo@latest hooks pre-task --description "task description"
npx ruflo@latest hooks post-task --task-id "<id>" --success true --store-results true
npx ruflo@latest hooks post-edit --file "path/to/file" --train-patterns
npx ruflo@latest hooks route --task "task description" --include-explanation

# Intelligence
npx ruflo@latest hooks pretrain --depth deep        # bootstrap on new/changed codebase
npx ruflo@latest hooks pretrain --model-type moe --epochs 10
npx ruflo@latest hooks intelligence stats
npx ruflo@latest hooks metrics
npx ruflo@latest hooks explain --topic "area of interest"
node .claude/helpers/hook-handler.cjs stats
node .claude/helpers/intelligence.cjs stats

# Worker dispatch
npx ruflo@latest hooks worker list
npx ruflo@latest hooks worker dispatch --trigger audit|map|optimize
npx ruflo@latest hooks worker status
```

### 12 Background Workers
`ultralearn` · `optimize` · `consolidate` · `predict` · `audit` · `map` · `preload` · `deepdive` · `document` · `refactor` · `benchmark` · `testgaps`

### Self-Learning Loop (runs automatically after every task)
```
RETRIEVE    → ReasoningBank.searchPatterns() via HNSW (150x–12,500x faster)
JUDGE       → confidence scoring, trigram/Jaccard similarity
DISTILL     → MemoryGraph PageRank, LoRA fine-tuning
CONSOLIDATE → EWC++ weight consolidation, HNSW upsert (prevents forgetting)
ROUTE       → Q-table update in QLearningRouter
```

---

## DAEMON

```bash
npx ruflo@latest daemon start                        # start at session begin
npx ruflo@latest daemon stop
npx ruflo@latest daemon status                       # shows worker history
npx ruflo@latest daemon trigger map|audit|optimize
npx ruflo@latest daemon enable map audit optimize
```

---

## DUAL-MODE COLLABORATION (Claude Code + Codex)

Run Claude Code and OpenAI Codex in parallel with shared memory. Claude for architecture/security/testing, Codex for implementation/optimization.

```bash
# Pre-built templates
npx claude-flow-codex dual run feature --task "task description"
npx claude-flow-codex dual run security --target "./src"
npx claude-flow-codex dual run refactor --target "./src/legacy"
npx claude-flow-codex dual run bugfix --task "task description"

# Custom split
npx claude-flow-codex dual run \
  --worker "claude:architect:Design the solution" \
  --worker "codex:coder:Implement it" \
  --worker "claude:tester:Write tests" \
  --namespace "feature-name"

# Shared memory across both platforms
npx ruflo@latest memory store --namespace collaboration --key "design" --value "..."
npx ruflo@latest memory search --namespace collaboration -q "relevant query"

# Train after successful collaboration
npx ruflo@latest hooks post-task --task-id "dual-session" --success true --train-neural true
```

---

## STACK REFERENCE

```
Orchestration: npx ruflo@latest  (NOT claude-flow for stable)
Swarms:        npx ruflo@latest swarm init --topology hierarchical --max-agents 8
Memory:        Beads (bd), Ruflo Memory, AgentDB (MCP tools), Native Tasks
Codebase:      GitNexus (npx gitnexus analyze)
Browser:       Ruflo's bundled browser tools (59 MCP tools, element refs, snapshots)
Observability: Ruflo session tracking + AttestationLog
Plugins:       agentic-qe, code-intelligence, test-intelligence, perf-optimizer, teammate, gastown-bridge
Specs:         OpenSpec (npx @fission-ai/openspec → os init, os)
```

### Ruflo Plugins
- **Agentic QE**: 58 QE agents — TDD, coverage, security scanning, chaos engineering
- **Code Intelligence**: code analysis, pattern detection, refactoring suggestions
- **Test Intelligence**: test generation, gap analysis, flaky test detection
- **Perf Optimizer**: performance profiling, bottleneck detection
- **Teammate Plugin**: bridges Native Agent Teams ↔ Ruflo swarms (21 MCP tools)
- **Gastown Bridge**: WASM-accelerated orchestration, Beads sync (20 MCP tools)
- **OpenSpec**: spec-driven development (`os init`, `os`)

---

## GOAL-TO-TASK PROTOCOL

When given an outcome statement:

1. **Boot memory** (session boot protocol above — skip if already booted this session)
2. **Route the goal**: `npx ruflo@latest hooks route "[goal]" --include-explanation`
3. **Recall prior solutions**: `npx ruflo@latest memory search -q "[keywords]" --limit 5`
4. **Search patterns**: `agentdb_pattern-search({ query: "[keywords]", limit: 5 })`
5. **Read files + check blast radius**: `gitnexus_impact` on every symbol you'll touch
6. **Generate ONE TodoWrite** with 5–10+ todos, parallel tasks clearly labeled
7. **Present plan**: "Found: [issues from memory + codebase]. Plan: [todos]. Proceed?" — wait for confirmation. (This is not "asking what to do" — you built the plan, you're confirming scope.)
8. **Execute**: parallel worktrees or `claude -p` for independent tasks
9. **Test**: run the project's test suite. If tests fail, fix before proceeding.
10. **After each task**: `npx ruflo@latest hooks post-task --task-id <id> --success true --store-results true`
11. **Store what you learned**: `ruv-remember` any patterns, fixes, or gotchas discovered
12. **Session end protocol**

---

## SECURITY

```bash
npx ruflo@latest security scan --depth full
npx ruflo@latest security audit|cve|threats|validate|report
```

Pre-edit hook always enforces: no hardcoded secrets, no mocks in production code, real implementations only, HTTPS protocols, validated user inputs.

---

## HEALTH CHECKS

```bash
npx ruflo@latest doctor --fix     # auto-diagnose and fix common issues
turbo-status                       # full TurboFlow stack health
turbo-help                         # all commands
rf-doctor                          # Ruflo health
node .claude/helpers/hook-handler.cjs stats
node .claude/helpers/intelligence.cjs stats
```

---

## FULL COMMANDS REFERENCE

```bash
# ── CORE ──────────────────────────────────────────────────────────
npx ruflo@latest init --wizard
npx ruflo@latest doctor --fix
npx ruflo@latest status

# ── DAEMON ────────────────────────────────────────────────────────
npx ruflo@latest daemon start|stop|status
npx ruflo@latest daemon trigger map|audit|optimize
npx ruflo@latest daemon enable <workers>

# ── MEMORY ────────────────────────────────────────────────────────
npx ruflo@latest memory store --namespace X --key Y --value Z
npx ruflo@latest memory search -q "query" --limit N
npx ruflo@latest memory retrieve --namespace X --key Y
npx ruflo@latest memory stats
ruv-remember "key" "value" | ruv-recall "query" | mem-search "query" | mem-stats

# ── HOOKS ─────────────────────────────────────────────────────────
npx ruflo@latest hooks session-start --session-id ${PROJECT_ID}
npx ruflo@latest hooks session-end --export-metrics true --persist-patterns true
npx ruflo@latest hooks session-restore --session-id ${PROJECT_ID}
npx ruflo@latest hooks route --task "description" --include-explanation
npx ruflo@latest hooks pre-task --description "description"
npx ruflo@latest hooks post-task --task-id X --success true --store-results true
npx ruflo@latest hooks post-edit --file X --train-patterns
npx ruflo@latest hooks pretrain --depth deep
npx ruflo@latest hooks intelligence stats | metrics
npx ruflo@latest hooks teammate-idle --auto-assign true
npx ruflo@latest hooks task-completed --task-id X --train-patterns true
npx ruflo@latest hooks worker list|dispatch|status
npx ruflo@latest hooks worker dispatch --trigger audit|map|optimize

# ── SWARM ─────────────────────────────────────────────────────────
npx ruflo@latest swarm init --topology star|hierarchical --max-agents N
npx ruflo@latest agent spawn -t coder|tester|reviewer|architect --name X
npx ruflo@latest task orchestrate "goal"

# ── HIVE-MIND ─────────────────────────────────────────────────────
npx ruflo@latest hive-mind init --topology hierarchical-mesh --consensus raft --name X
npx ruflo@latest hive-mind spawn --agents N --strategy specialized
npx ruflo@latest hive-mind status
npx ruflo@latest hive-mind resume --name X

# ── NEURAL ────────────────────────────────────────────────────────
npx ruflo@latest neural train|status|patterns|predict|optimize

# ── SECURITY / PERFORMANCE ────────────────────────────────────────
npx ruflo@latest security scan --depth full
npx ruflo@latest security audit|cve|threats|validate|report
npx ruflo@latest performance benchmark --suite all
npx ruflo@latest performance profile|metrics|optimize|report

# ── PLUGINS ───────────────────────────────────────────────────────
npx ruflo@latest plugins list
npx ruflo@latest plugins install|enable|disable @claude-flow/plugin-name

# ── BEADS ─────────────────────────────────────────────────────────
bd ready | bd ready --json
bd add --type issue|blocker|decision "text"
bd update <id> --claim | bd close <id>
bd list --type <type> | bd show <id>
bd dolt push

# ── WORKTREES ─────────────────────────────────────────────────────
wt-add <n> | wt-remove <n> | wt-list | wt-clean

# ── QUALITY ───────────────────────────────────────────────────────
aqe-generate | aqe-gate | os-init | os

# ── HEALTH ────────────────────────────────────────────────────────
turbo-status | turbo-help | rf-doctor
npx ruflo@latest doctor --fix
```

---

## PROJECT CONTEXT
<!-- Fill in this section for each project. Everything above is universal. -->

### Project ID
```
PROJECT_ID=your-project-name
```
> Replace all `${PROJECT_ID}` references in the session boot/end protocols above with this value.

### Tech Stack
```
Framework:
Language:
Database:
Auth:
Storage:
Deploy:
UI:
State:
Payments:
AI/LLM:
i18n:
```

### Deployment Environment Variables
```
# List all required env vars for production deployment
# NEVER put actual values here — this file is committed to git
VAR_NAME=description of what this is
```

### Known Issues
```
# Document active bugs and incomplete features here
# Update this list as issues are resolved or discovered
# Format: file path — description
```

### Architecture Decisions
```
# Key decisions that affect how agents should approach this codebase
# Add entries as decisions are made during development
# Format: date — decision — rationale
```

---

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report blast radius before any edit.
- **MUST run `gitnexus_detect_changes()` before committing** to verify changes match expected scope.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk.
- Use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping.
- Use `gitnexus_context({name: "symbolName"})` for full callers/callees/flows on any symbol.

## When Debugging
1. `gitnexus_query({query: "<symptom>"})` — find related execution flows
2. `gitnexus_context({name: "<suspect>"})` — callers, callees, process participation
3. `READ gitnexus://repo/${PROJECT_ID}/process/{processName}` — trace full execution
4. Regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})`

## When Refactoring
- **Renaming**: `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` first, then `dry_run: false`
- **Extracting**: `gitnexus_context` + `gitnexus_impact` before moving any code
- **After any refactor**: `gitnexus_detect_changes({scope: "all"})` to verify scope

## Never Do
- NEVER edit without running `gitnexus_impact` first
- NEVER ignore HIGH or CRITICAL risk warnings
- NEVER rename with find-and-replace — use `gitnexus_rename`
- NEVER commit without `gitnexus_detect_changes`

## Tools Quick Reference
| Tool | When | Command |
|------|------|---------|
| `query` | Find code by concept | `gitnexus_query({query: "..."})` |
| `context` | 360° view of symbol | `gitnexus_context({name: "..."})` |
| `impact` | Blast radius | `gitnexus_impact({target: "...", direction: "upstream"})` |
| `detect_changes` | Pre-commit check | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | Safe rename | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | Custom graph queries | `gitnexus_cypher({query: "MATCH ..."})` |

## Risk Levels
| Depth | Meaning | Action |
|-------|---------|--------|
| d=1 | WILL BREAK — direct callers | MUST update these |
| d=2 | LIKELY AFFECTED | Should test |
| d=3 | MAY NEED TESTING | Test if critical path |

## Resources
| Resource | Use for |
|----------|---------|
| `gitnexus://repo/${PROJECT_ID}/context` | Codebase overview |
| `gitnexus://repo/${PROJECT_ID}/clusters` | All functional areas |
| `gitnexus://repo/${PROJECT_ID}/processes` | All execution flows |
| `gitnexus://repo/${PROJECT_ID}/process/{name}` | Step-by-step trace |

## Self-Check Before Finishing
1. `gitnexus_impact` was run for all modified symbols
2. No HIGH/CRITICAL warnings were ignored
3. `gitnexus_detect_changes()` confirms scope matches expectation
4. All d=1 dependents were updated

## Keeping the Index Fresh
```bash
npx gitnexus analyze
# Preserve embeddings if they exist:
npx gitnexus analyze --embeddings
# Check: cat .gitnexus/meta.json | grep embeddings
```
> A PostToolUse hook updates the index automatically after `git commit` and `git merge`.

## Skill Files
| Task | Skill file |
|------|-----------|
| Understand architecture | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius analysis | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools and schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, wiki CLI | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
