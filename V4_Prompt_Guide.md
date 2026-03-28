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

### Log a decision
```
Log a decision: we're using DB-based rate limiting instead of Redis because the project doesn't have a Redis instance.
```
→ Creates a bead

### Log a blocker
```
Log a blocker: can't test invitation emails without an SMTP service configured.
```

### Check on things
```
What's the current status? Show me the full board.
```
```
What blockers are open?
```
```
What patterns have we stored this session?
```
```
How's the GitNexus index — is it fresh?
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

That triggers the full session end protocol — persists learning, stores summary, trains patterns, files beads, runs daemon audit.

If you need to leave quickly:
```
Quick save and end. We'll pick up next session.
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

## The One Rule

You describe **what** you want. Not **how** to do it.

Bad: "Open src/lib/permissions.ts, go to line 42, change the return value from 0 to the actual count"
Good: "AI call tracking is hardcoded to 0. Make it use real data."

The system has 5 layers of memory, a code graph, pattern matching, and 259 MCP tools. Let it figure out the how.
