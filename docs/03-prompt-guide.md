# TurboFlow Prompt Guide
> Quick reference. Your CLAUDE.md has the full details — this is what you actually type.

---

## 1. START A SESSION

Paste this as your first message every time:

```
Boot up. Project ID is [your-project-name]. Run the full session boot protocol, show me the status board when done.
```

That's it. The CLAUDE.md runs the full 11-step primer automatically:

```
Step 0:  Pre-flight     — env file, migrations, stashes, disk space
Step 1:  Daemon          — starts background workers
Step 2:  Hooks           — verifies registration, fires session-start (restores context from SQLite)
Step 3:  Beads           — loads all open issues, blockers, decisions
Step 4:  Intelligence    — checks if warm, auto-runs pretrain if cold
Step 5:  Ruflo Memory    — verifies HNSW index health, then recalls project state
Step 6:  AgentDB         — health check probe via MCP, auto-repairs if unavailable
Step 7:  GitNexus        — checks freshness, auto-reindexes if stale (not optional)
Step 8:  Swarm           — initializes star topology
Step 9:  Security        — verifies pre-edit hooks and audit worker are active
Step 10: Router          — routes today's work via Q-learning
```

Every subsystem gets primed, not just checked. If anything is broken, it auto-fixes and reports what it did.

If resuming a previous session:

```
Boot up. Project ID is [your-project-name]. Resume from last session — check memory and beads for where we left off.
```

### After boot: Full branch analysis

Once the status board is green, paste this to get a complete picture of where the branch stands and what needs to happen:

```
Run a full branch analysis. I need to know exactly where we are and what's left to do.

1. BRANCH STATE — what branch, how far ahead/behind main, full diff summary vs main, uncommitted changes, stashes, last 10 commits with timestamps

2. CODEBASE CHANGES — run gitnexus_detect_changes vs main, what symbols changed, what execution flows are affected, any HIGH/CRITICAL risk

3. BEADS STATUS — open issues, blockers, recently completed, anything flagged for human decision, run bd lint

4. MEMORY RECALL — search memory for recent sessions, known blockers, AgentDB patterns related to current work, logged decisions

5. HEALTH CHECK — run tests, build, and lint right now. Check for pending migrations and missing env vars.

6. QUALITY ENGINEERING — run aqe-gate on the branch. Show test coverage gaps, security scan results, and any quality issues found. If tests are missing for changed files, flag them.

7. GAP ANALYSIS — based on everything above, what is DONE, IN PROGRESS, and NOT STARTED? What's blocking? What can be parallelized?

Then give me:
A. STATUS SUMMARY — 5-10 lines, plain English
B. PRIORITIZED TODO — generate a TodoWrite ordered by priority and dependency, include any aqe-gate findings as tasks
C. SESSION PLAN — if I have 2-4 hours, what do we tackle first?
```

This runs ~20-25 tool calls across git, gitnexus, beads, memory, agentdb, agentic-qe, and your test suite. Takes about 2-3 minutes. After that you say "proceed" and start working.

**The short version** if you don't need the full analysis:
```
What's the state of this branch? Quick summary, open beads, and what should we work on.
```

---

## 2. GIVE IT WORK

You describe outcomes. It generates the plan. You approve. It executes.

**Single task:**
```
Add rate limiting to the /api/invitations endpoint. 10 per hour per agency. Use DB count, no Redis.
```

**Multi-task (it will parallelize automatically):**
```
I need three things done:
1. AI call tracking — enforce quota per tier
2. Quota reset cron job — monthly, batch processing
3. Client-side permission hooks — usePermissions, useQuota, useFeatureGate

Parallel where possible.
```

**Vague goal (it will research and plan):**
```
The team invitation flow doesn't work yet. Make it work end to end — invites, acceptance, seat limits, the UI.
```

**What happens:** It recalls prior solutions from memory + AgentDB → reads code + checks blast radius → generates a TodoWrite → shows you the plan → waits for your "proceed" → executes in parallel → runs tests → stores what it learned.

### Batch execution from ADR/DDD

After you've completed your ADR/DDD planning and have a structured list of work items, paste this to execute them all sequentially without stopping between items:

```
Execute the following batch in order. For each item:
- Read the relevant files first
- Run gitnexus_impact on symbols you'll touch
- Implement the change
- Run tests after each item
- Log a bead when done (bd close or bd create for discovered work)
- Store any patterns learned (ruv-remember)
- Show the Status HUD after each item completes
- Do NOT stop to ask between items — only stop if tests fail or you hit a blocker

If any item fails or creates a conflict, log it as a blocker bead and continue to the next independent item. At the end, give me a summary of what completed, what failed, and what needs attention.

BATCH:
1. [ADR-001] — [description of what to implement]
2. [ADR-002] — [description of what to implement]
3. [ADR-003] — [description of what to implement]
4. [ADR-004] — [description of what to implement]
5. [ADR-005] — [description of what to implement]
...
```

**Tips for writing good batch items:**
- Each item should be one bounded context or one ADR — not "build the whole app"
- Order by dependency — items that others depend on go first
- Include the ADR number so the agent can reference your planning docs
- If items are independent, say so — the agent will parallelize with worktrees

**Short version** when you already have beads for everything:
```
Execute all ready beads in dependency order. Don't stop between items. Log results. Summary at the end.
```

**From a plan file:**
```
Read plans/research/PLAN.md. Execute every ADR in order as a batch. Don't stop between items unless tests fail. aqe-gate after each context. Summary at the end.
```

---

## 3. DURING A SESSION

### Remember something for future sessions
```
Remember that the agency slug field was removed in the RBAC migration — invitations.ts needs to use agency.id instead.
```
→ Stores to Ruflo Memory + Beads

### Recall past solutions
```
What did we do last time to fix the permission middleware? Search memory.
```

### Create an issue for something you found
```
Create a bug: the quota reset doesn't handle users with no subscription. Priority 1, link it to the current work.
```
→ Uses `bd create` with proper type, priority, and `discovered-from` linking

### Log a decision
```
Log a decision: we're using DB-based rate limiting instead of Redis because the project doesn't have a Redis instance.
```

### Log a blocker
```
Create a blocker: can't test invitation emails without an SMTP service configured. Priority 0.
```

### Flag something for your review
```
Flag bd-42 for human decision — I need to look at this myself.
```

### Check on things
```
What's the current status? Show me the full board.
```
```
What's ready to work on?
```
```
Show all open blockers.
```
```
Run beads hygiene — check for stale issues and orphans.
```
```
What patterns have we stored this session?
```

---

## 4. PARALLEL WORK

### Spawn agents for independent tasks
```
Spin up a team for this sprint:
- Agent 1: Build the InviteMemberModal component
- Agent 2: Build the MemberList component
- Agent 3: Write tests for both

Use worktrees. Run in parallel.
```

### Spawn agents for a larger effort
```
I need a 4-agent swarm:
- Architect: Design the billing page data flow
- Coder-1: Build SubscriptionCard and QuotaProgressBar components
- Coder-2: Build the TierSelector component
- Tester: Write integration tests as components land

Hierarchical topology. Architect leads.
```

### Multi-day sprint (persists across terminal closes)
```
Initialize a hive-mind sprint called "rbac-ui-build". 4 agents, specialized strategy, raft consensus. This will span multiple sessions.
```

To resume next session:
```
Resume the hive-mind sprint "rbac-ui-build". Show me where each agent left off.
```

---

## 5. CODE REVIEW & SAFETY

### Before merging
```
Show me what's changed on this branch compared to main. Run impact analysis on all modified symbols.
```

### Review staged changes
```
Review everything I've staged. Flag bugs, missing error handling, type issues, security concerns.
```

### Check blast radius before a refactor
```
I want to rename handleTierUpgrade to processTierUpgrade. Show me the blast radius before we do anything.
```

### Run tests
```
Run the full test suite and show me results.
```
You shouldn't need to say this often — the CLAUDE.md requires tests before every commit. But if you want to check manually.

### Security scan
```
Run a full security scan on the project.
```

### Before a dangerous operation
The agent will auto-confirm with you before running destructive commands (`git reset --hard`, `rm -rf`, `DROP TABLE`, etc.) on any branch. You don't need a special prompt — just say yes or no when it asks.

---

## 6. WHEN THINGS BREAK

### Something's not working in the TurboFlow stack
```
Run doctor and fix whatever's broken.
```

### Specific subsystem down
```
AgentDB is returning unavailable. Fix it.
```
```
GitNexus index is stale. Reindex now.
```
```
Intelligence is cold — no patterns loaded. Pretrain.
```
```
Hooks aren't firing. Check registration and fix.
```
The boot protocol auto-fixes most of these, but if something goes down mid-session, just name it.

### Agent seems to have lost context
```
Context seems stale. Restore from the session archive and show me what was recovered.
```

### A merge broke main
```
Main is broken after the last merge. Revert it, show me what went wrong.
```
→ It follows the rollback protocol: revert → verify → commit → push → report → bead

### Stuck on a problem
Don't need to say anything — the CLAUDE.md tells it to stop after 3 failed attempts and explain what it tried. But if you notice it spinning:
```
Stop. What have you tried so far and why isn't it working?
```

---

## 7. END A SESSION

```
End session. Store what we did, what we learned, and what's next.
```

That triggers the full session end protocol: file remaining work as beads → run quality gates (tests/lint/build) → persist learning → store summary → sync beads → **git push** → daemon audit.

**The agent will not stop until `git push` succeeds.** This is enforced in the CLAUDE.md — work stranded locally is work lost.

If you need to leave quickly:
```
Quick save and end. Push everything now.
```

---

## 8. HEALTH & STATUS COMMANDS

These are for when you want to manually check something specific:

| What you want | What to say |
|---|---|
| Full system status | `Show me the full status board` |
| What's running | `Daemon status and worker list` |
| Memory stats | `How many patterns and memories are stored?` |
| AgentDB status | `Are all AgentDB controllers online?` |
| Open issues | `Show all open beads` |
| Blockers | `What blockers are open?` |
| GitNexus freshness | `Is the GitNexus index current?` |
| Intelligence stats | `Show intelligence and hook stats` |
| Security hooks | `Are pre-edit hooks and audit worker active?` |
| Context health | `How many turns are archived? Is context autopilot running?` |
| Test status | `When did tests last run? Are they passing?` |
| Session cost | `How much have we spent this session?` |
| Disk / env health | `Run pre-flight checks again` |
| Everything at once | `Full health check — run doctor and show all stats` |

But normally you don't need these — the Status HUD shows everything after every action.

---

## 9. MODEL ROUTING

You don't usually need to manage this — the Q-learning router picks the right model. But you can override:

```
Use Opus for this — it's a complex architecture decision.
```
```
This is just formatting cleanup, use Haiku.
```

---

## 10. QUICK PATTERNS

**"I want to explore two approaches"**
```
Fork this into two parallel attempts:
- Approach A: [description]
- Approach B: [description]
Show me both results and let me pick.
```

**"Do this but don't touch X"**
```
Refactor the permission middleware but do NOT modify the User model or any migration files.
```

**"I changed my mind mid-task"**
```
Stop current work. Stash changes. Let's rethink this.
```

**"Show me before you change anything"**
```
Plan only — don't execute. Show me the TodoWrite and wait for approval.
```

**"Just do it, I trust you"**
```
Execute the full plan. No confirmation needed on individual steps — just the final merge gate.
```

---

## What's Automatic vs What You Trigger

### Tier 1: Truly automatic — fires without anyone doing anything
Hooks registered in `.claude/settings.json`. No one chooses to run these — they fire on events:
- **Context Autopilot** — archives every turn, blocks context loss, restores on session start
- **Pre-edit verification** — checks for secrets, mocks in prod, HTTPS before any file write
- **Post-edit learning** — records outcomes, updates Q-table routing after every edit
- **GitNexus auto-index** — re-indexes after `git commit` and `git merge`
- **Intelligence routing** — Q-learning picks Opus/Sonnet/Haiku per task automatically
- **Agent Booster** — WASM transforms (var-to-const, add-types) skip LLM entirely, $0

### Tier 2: Agent follows CLAUDE.md rules — you don't need to ask
The CLAUDE.md says "MUST" and the agent obeys. You never need to say "use gitnexus" or "check beads" — these happen because the rules require them:
- `gitnexus_impact` before editing any symbol
- `gitnexus_detect_changes` before committing
- `agentdb_pattern-search` before solving any bug
- Beads for all issue tracking (no markdown TODOs)
- Tests before every commit
- Status HUD after every action
- Triple-Gate for merges to main
- Mandatory `git push` at session end
- 3-strikes escalation (stop after 3 failed attempts)

### Tier 3: You trigger it — agent executes
These need you to say something:
- **Swarm/Agent Teams** — "spin up a swarm" or "spawn 3 reviewers"
- **Hive-Mind** — "initialize a multi-day sprint"
- **Batch execution** — you paste the batch prompt with your ADR list
- **Full aqe-gate** — agent runs it per-context automatically, but you decide when to gate the full codebase
- **Branch analysis** — you paste the analysis prompt post-boot

**Bottom line:** After boot, you describe outcomes. Tier 1 runs silently. Tier 2 runs because the CLAUDE.md tells the agent to. You only manually trigger Tier 3 when you need parallel work, batch runs, or full-codebase quality gates.

---

## The One Rule

You describe **what** you want. Not **how** to do it.

Bad: "Open src/lib/permissions.ts, go to line 42, change the return value from 0 to the actual count"
Good: "AI call tracking is hardcoded to 0. Make it use real data."

The system has 5 layers of memory, a code graph, pattern matching, and 259 MCP tools. Let it figure out the how.
