# Ruflo → Strands Migration Evaluation

Assessment of replacing Ruflo v3.5 with Strands Agents as TurboFlow's orchestration layer.

---

## Capability Matrix

| Capability | Ruflo (current) | Strands (built) | Status |
|---|---|---|---|
| **Orchestration** | | | |
| Multi-agent swarms | `rf-swarm` (hierarchical, mesh, ring, star) | `create_team()` (supervisor-agent pattern) | ✅ Covered — hierarchical via supervisor. Mesh/ring/star possible via Strands graphs but not pre-built. |
| Agent spawning | `rf-spawn coder` | `create_agent("coder")` | ✅ Covered — 7 pre-configured types |
| Agent types | 60+ types | 7 types (coder, tester, reviewer, architect, researcher, coordinator, security) | ⚠️ Partial — only the 7 most-used types. Others can be added. |
| Task delegation | Ruflo task routing | Strands agents-as-tools | ✅ Covered — native pattern |
| Daemon mode | `rf-daemon` | Not applicable | ➖ Not needed — Strands agents are invoked programmatically |
| Init / wizard | `rf-init`, `rf-wizard` | Not applicable | ➖ Not needed — no `.claude-flow/` directory required |
| Doctor / diagnostics | `rf-doctor` | `tf-adapter health --backend strands` | ✅ Covered |
| **Model Routing** | | | |
| 3-tier auto-routing | Ruflo selects opus/sonnet/haiku | `select_tier(task)` | ✅ Covered — keyword + length heuristics |
| Cost optimization | ~75% savings claimed | Same tiers, same savings | ✅ Equivalent |
| **Memory** | | | |
| AgentDB (vector store) | `ruv-remember`, `ruv-recall`, `ruv-stats` | Not built | ❌ Gap — no vector store equivalent. Beads covers structured memory but not semantic search. |
| Ruflo native memory | `mem-search`, `mem-store`, `mem-stats` | Not built | ❌ Gap — same as above. |
| Beads integration | Via CLI | 4 Beads tools built into every agent | ✅ Improved — agents auto-check Beads |
| **Plugins** | | | |
| Agentic QE (58 agents) | `aqe-generate`, `aqe-gate` | Security audit team recipe | ⚠️ Partial — security-audit team covers review + security. Missing: TDD generation, coverage analysis, chaos engineering, flaky test detection. |
| Code Intelligence | `plugins run code-intelligence` | Reviewer agent + GitNexus | ⚠️ Partial — code review via agent, codebase analysis via GitNexus. Missing: pattern detection, refactoring suggestions as automated pipeline. |
| Test Intelligence | `plugins run test-intelligence` | Tester agent | ⚠️ Partial — tester writes tests. Missing: gap analysis, flaky test detection as automated tools. |
| Perf Optimizer | `plugins run perf-optimizer` | Not built | ❌ Gap — no performance profiling or bottleneck detection. |
| Teammate Plugin | Bridges Agent Teams ↔ Ruflo | Not applicable | ➖ Not needed — Strands has its own multi-agent. |
| Gastown Bridge | WASM orchestration, Beads sync | Not applicable | ➖ Not needed — Strands is native Python. |
| **Hooks Intelligence** | | | |
| Pre/post edit hooks | `hooks-pre`, `hooks-post` | Not built | ❌ Gap — no automatic pre/post edit analysis. Could be built as Strands tools. |
| Hook training | `hooks-train` | Not built | ❌ Gap |
| Hook routing | `hooks-route` | Not built | ❌ Gap |
| **Neural** | | | |
| Neural training | `neural-train` | Not built | ❌ Gap — no pattern learning from past executions. |
| Neural patterns | `neural-patterns` | Not built | ❌ Gap |
| Neural status | `neural-status` | Not built | ❌ Gap |
| **Codebase Intelligence** | | | |
| GitNexus MCP | Via Claude Code MCP | 4 CLI tools + MCP client | ✅ Covered |
| Blast radius | Via GitNexus MCP | `gitnexus_tools(use_mcp=True)` | ✅ Covered |
| **Observability** | | | |
| Statusline Pro | 15-component bash statusline | OTEL traces + metrics + cost estimation | ✅ Improved — structured telemetry vs terminal display |
| Cost tracking | Via statusline | `estimate_cost()` + `track_execution()` | ✅ Covered |
| Session tracking | Ruflo built-in | OTEL spans per agent invocation | ✅ Covered |
| **Agent Isolation** | | | |
| Git worktrees | `wt-add`, `wt-remove` | Not built into Strands layer | ⚠️ Gap — worktree helpers exist as shell aliases but not as Strands tools. Agents can use `run_command` to create worktrees. |
| PG Vector schema isolation | `DATABASE_SCHEMA` env var | Not applicable | ➖ Not needed without AgentDB |
| **MCP Tools** | | | |
| 215 MCP tools | Via Ruflo + Claude Code | Via Strands native MCP | ✅ Covered — Strands supports MCP natively. Same tools available. |
| Browser tools (59) | Bundled in Ruflo | Not bundled | ⚠️ Gap — browser automation tools not included. Available via MCP if needed. |
| **Deployment** | | | |
| Container only | Docker / K8s | Lambda, Fargate, ECS, Bedrock AgentCore | ✅ Improved — more deployment options |
| **Licensing** | | | |
| Ruflo | Third-party npm (risk #1) | N/A | |
| Strands | N/A | Apache-2.0, AWS-backed | ✅ Eliminated risk |
| Claude Code | Proprietary binary (risk #2) | Not required for Strands | ✅ Eliminated risk |

---

## Summary

### What Strands covers well (ready to replace Ruflo)

- Multi-agent orchestration (supervisor-agent pattern)
- Agent spawning with pre-configured types
- Model routing (auto tier selection)
- Beads integration (improved — built into every agent)
- GitNexus integration (CLI + MCP)
- Observability (improved — OTEL vs bash statusline)
- MCP tool support (native)
- Cost tracking and estimation

### Gaps that need work before full replacement

| Gap | Impact | Effort to build | Priority | Status |
|---|---|---|---|---|
| AgentDB / vector memory | Medium | Medium | P2 | ✅ Built — SQLite + Bedrock Titan Embeddings, 3 tools (remember, recall, stats) |
| Agentic QE depth | Medium | Medium | P2 | ✅ Built — 3 new recipes: TDD, coverage-analysis, qa-gate |
| Hooks intelligence | Low | Low | P3 | Not started |
| Neural training | Low | Medium | P3 | Not started |
| Perf optimizer | Low | Medium | P3 | Not started |
| Browser automation | Low | Low | P3 | Not started |
| Git worktree tools | Low | Low | P3 | Not started |

### Recommendation

Strands can replace Ruflo for the core workflow today: agent spawning, multi-agent teams, model routing, memory, codebase intelligence, and observability. The gaps are in advanced features (AgentDB, neural training, hooks intelligence) that most users don't use daily.

**Migration path:**
1. **Now:** Use Strands for all new programmatic/automated work. Keep Ruflo CLI for interactive use.
2. **Next:** Add AgentDB equivalent (vector memory) and deeper QE recipes.
3. **Later:** Build hooks intelligence and neural training if usage data shows demand.
4. **Eventually:** Deprecate Ruflo aliases, point them to Strands equivalents.

The existing Ruflo CLI (`rf-*` aliases) continues to work unchanged. No breaking changes. Strands is additive until the gaps are filled.
