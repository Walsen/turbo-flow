# Agent Instructions

See `CLAUDE.md` for full rules, memory system details, and project context.

**Primary model: GLM-5.1.** 200K context, 131K max output. Generate complete new files in one pass. Use `--json` on all `bd` commands.

## Prime Directive

**Search memory BEFORE starting. Store patterns AFTER success. Fix bugs autonomously — don't ask for hand-holding.**

```
1. agentdb_pattern-search / mem-search     → Check for known solutions
2. bd ready --json                         → Find available work
3. Plan if 3+ steps, then EXECUTE          → Write code, run commands
4. Verify it works (tests, logs, diff)     → Prove correctness
5. agentdb_pattern-store / memory store    → Remember what worked
6. bd close <id> --reason "..." --json     → Record what was done + proof
```

After ANY correction from the human: `bd remember "lesson/<topic>" "what went wrong and the rule"`

---

## Beads Quick Reference

Use `bd` for ALL tracking. NOT `beads`. NOT TodoWrite. NOT markdown TODOs. Every `bd create` needs `--description` with full context.

```bash
bd ready --json                          # Find unblocked work
bd update <id> --claim --json            # Claim before starting
bd comments add <id> "progress" --json   # Record findings mid-task
bd close <id> --reason "what+why" --json # Complete (after proving it works)
bd create "Title" --description="..." -t bug|feature|task -p 0-4 --json
bd remember "key" "value"                # Persistent knowledge
bd dolt push                             # Sync to remote
```

Types: `bug` · `feature` · `task` · `epic` · `chore` — Priorities: `0` critical → `4` backlog

---

## Agent Types

| Type | Purpose |
|------|---------|
| `system-architect` | Design systems, architectural decisions |
| `coder` | Write implementation code |
| `tester` | Write and run tests |
| `reviewer` | Code quality and security review |
| `researcher` | Investigate bugs, analyze requirements |
| `coordinator` | Orchestrate multi-agent work |
| `security-architect` | Security design and audit |

## Swarm Recipes

Always hierarchical topology. Spawn ALL agents in ONE message. One task per subagent.

**Feature (5 agents):**
```bash
npx ruflo@latest swarm init --topology hierarchical --max-agents 8 --strategy specialized
Task("Architect", "Design [feature]. Store design in memory.", "system-architect")
Task("Coder-1", "Implement [part A].", "coder")
Task("Coder-2", "Implement [part B].", "coder")
Task("Tester", "Write tests.", "tester")
Task("Reviewer", "Review quality + security.", "reviewer")
```

**Bug Fix (3 agents):**
```bash
npx ruflo@latest swarm init --topology hierarchical --max-agents 4 --strategy specialized
Task("Researcher", "Investigate. Check agentdb for known patterns.", "researcher")
Task("Coder", "Fix based on findings.", "coder")
Task("Tester", "Write regression test + verify.", "tester")
```

Agent Teams requires API key in `~/.bashrc` — verify: `echo $ANTHROPIC_API_KEY`

---

## Non-Interactive Shell

**ALWAYS use non-interactive flags** — aliased `-i` hangs agents.

```bash
cp -f source dest         mv -f source dest         rm -f file
rm -rf directory          cp -rf source dest
```

`apt-get -y` · `scp -o BatchMode=yes` · `HOMEBREW_NO_AUTO_UPDATE=1 brew`

---

## Session Completion

Work is NOT complete until `git push` succeeds. NEVER say "ready to push when you are" — YOU push.

1. `bd create` remaining work (with `--description`)
2. `bd close` finished work (with `--reason` explaining what + proof)
3. Quality gates: `npm test && npm run build` + `aqe-gate`
4. Store learnings: `npx ruflo@latest hooks session-end --export-metrics true --persist-patterns true`
5. Push:
   ```bash
   bd dolt push && git pull --rebase && git push
   git status  # MUST show "up to date with origin"
   ```
