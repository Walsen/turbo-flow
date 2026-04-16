# TurboFlow — Multi-Agent Agentic Development Platform

<div align="center">

![Version](https://img.shields.io/badge/version-4.1.0-blue?style=for-the-badge)
![Strands](https://img.shields.io/badge/Strands_Agents-1.35-purple?style=for-the-badge)
![Bedrock](https://img.shields.io/badge/Amazon_Bedrock-native-orange?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Adventure Wave Labs](https://img.shields.io/badge/Adventure_Wave_Labs-Builder-ff6b6b?style=for-the-badge)

**AI coding agents with cross-session memory, codebase intelligence, and multi-agent teams.**

**Run locally or deploy to AWS with one command.**

*Built & Presented by [Adventure Wave Labs](https://www.adventureonthewave.com/#projects)*

[Quick Start](#quick-start) • [Agent Types](#agent-types) • [Team Recipes](#team-recipes) • [CLI Reference](#cli-reference) • [Deploy to Cloud](#deploy-to-cloud) • [Architecture](#architecture)

</div>

---

## About Adventure Wave Labs

<div align="center">
  <img src="https://i.ibb.co/N6m72sYQ/AWLabs.png" alt="Adventure Wave Labs" width="600">
</div>

**Adventure Wave Labs** is the team behind TurboFlow — a complete agentic development environment built for the Claude ecosystem. We design, build, and maintain the tooling that brings together orchestration, memory, codebase intelligence, and agent isolation into a single streamlined workflow.

---

## What is TurboFlow?

TurboFlow is a platform for running AI coding agents that:

- **Remember across sessions** — Beads tracks decisions, patterns, and work items. AgentDB provides semantic search over past solutions.
- **Understand your codebase** — GitNexus builds a knowledge graph of dependencies, call chains, and blast radius.
- **Work as teams** — Multi-agent recipes (feature, bug-fix, code-review, security-audit, TDD, QA gate) coordinate specialists automatically.
- **Route to the right model** — Auto-selects Opus for architecture, Sonnet for coding, Haiku for simple tasks. Saves 40-75% on API costs.
- **Run anywhere** — Same code runs locally (Python) or deployed to AWS (Bedrock AgentCore). One `tf` command for both.

---

## Quick Start

### Prerequisites

- Python 3.10+ and [uv](https://docs.astral.sh/uv/getting-started/installation/)
- AWS credentials with Bedrock access (for model calls)

### Install

```bash
git clone https://github.com/Walsen/turbo-flow
cd turbo-flow/agent-adapter/python
uv sync --extra strands
```

### Configure

```bash
# Copy the environment template and fill in your values
cp .envrc.template .envrc
direnv allow .

# At minimum, set your AWS profile and region in .envrc:
#   export AWS_PROFILE=your-profile
#   export CLAUDE_CODE_USE_BEDROCK=1
#   export AWS_REGION=us-east-1
```

### Run your first agent

```bash
# Via CLI
uv run tf "Write a Python function to merge two sorted lists"

# Via Python
python -c "
from turboflow_adapter.strands import create_agent
agent = create_agent('coder')
print(agent('Write a Python function to merge two sorted lists'))
"
```

---

## Agent Types

Pre-configured agents with tuned system prompts, default model tiers, and TurboFlow tools built in.

| Type | Default Model | What it does |
|---|---|---|
| `coder` | Sonnet | Writes implementation code. Has file tools + Beads. |
| `tester` | Sonnet | Writes tests, covers edge cases and error paths. |
| `reviewer` | Sonnet | Reviews code for correctness, security (CWE IDs), performance. |
| `system-architect` | Opus | Designs systems with trade-off analysis. Records decisions in Beads. |
| `researcher` | Sonnet | Investigates bugs, analyzes requirements, gathers evidence. |
| `coordinator` | Opus | Orchestrates multi-agent work, tracks progress via Beads. |
| `security-architect` | Opus | Audits for OWASP Top 10, rates severity, provides remediation. |

```python
from turboflow_adapter.strands import create_agent

# Each agent comes with the right model, prompt, and tools
coder = create_agent("coder")
reviewer = create_agent("reviewer")
architect = create_agent("system-architect")

# Override model tier if needed
cheap_coder = create_agent("coder", model_tier="haiku")
powerful_coder = create_agent("coder", model_tier="opus")
```

---

## Team Recipes

Multi-agent teams using the supervisor pattern. One line creates a supervisor that delegates to specialists.

| Recipe | Agents | Use case |
|---|---|---|
| `feature` | architect + coder + tester + reviewer | Implement a new feature end-to-end |
| `bug-fix` | researcher + coder + tester | Investigate, fix, and write regression test |
| `code-review` | reviewer + security architect | Code quality + security audit |
| `security-audit` | security architect + researcher + reviewer | Full OWASP audit with severity ratings |
| `full-build` | architect + coder + tester + reviewer + security | Design → build → test → review → security |
| `tdd` | researcher + tester + coder | Tests first, then implement to pass |
| `coverage-analysis` | researcher + tester | Find test gaps, generate missing tests |
| `qa-gate` | reviewer + tester + security | PASS/FAIL verdict for merge readiness |

```python
from turboflow_adapter.strands import create_team

# One line — supervisor coordinates the specialists
team = create_team("feature")
result = team("Add rate limiting middleware to the Express API")

# QA gate before merging
gate = create_team("qa-gate")
result = gate("Check the current branch for merge readiness")

# Full application build
team = create_team("full-build")
result = team("Build a bookmark manager API with FastAPI and SQLite")
```

---

## CLI Reference

The `tf` command works locally and in the cloud. If `TURBOFLOW_RUNTIME_ARN` is set, it routes to your deployed agent on AgentCore. Otherwise it runs locally via Strands.

```bash
# Basic usage
tf "Write a fibonacci function"

# Specific agent type
tf -a reviewer "Review src/auth.py for security issues"
tf -a system-architect "Design a notification system"

# Multi-agent team
tf --team feature "Add user registration with email verification"
tf --team qa-gate "Check this PR for merge readiness"
tf --team full-build "Build a task management API"

# Model override
tf -m haiku "Fix the typo in README"          # cheapest
tf -m opus "Design event-driven architecture"  # most capable

# Force local or cloud
tf --local "prompt"                            # always local (Strands)
tf --cloud "prompt"                            # always cloud (AgentCore)
tf --local -b aider "prompt"                   # specific local backend

# Status and health
tf status                                      # local + cloud status
tf health                                      # health check
tf backends                                    # list available backends
```

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `CLAUDE_CODE_USE_BEDROCK` | — | Set to `1` to use Amazon Bedrock |
| `AWS_REGION` | `us-east-1` | AWS region for Bedrock |
| `TURBOFLOW_AGENT_BACKEND` | `claude` | Default local backend |
| `TURBOFLOW_RUNTIME_ARN` | — | AgentCore Runtime ARN (enables cloud mode) |
| `TF_ADAPTER_LOG_LEVEL` | `INFO` | Log level: DEBUG, INFO, WARN, ERROR |

---

## Auto Model Routing

TurboFlow automatically selects the cheapest model that can handle the task:

```python
from turboflow_adapter.strands import select_tier

select_tier("Fix typo in README")                    # → haiku ($)
select_tier("Implement JWT token refresh")           # → sonnet ($$)
select_tier("Design CQRS event-sourcing architecture") # → opus ($$$)
```

This saves 40-75% on Bedrock costs compared to using Sonnet for everything.

---

## Memory

### Beads (cross-session project memory)

Every agent automatically checks Beads at session start and records work when done.

```bash
bd ready              # Check project state
bd create "title" -t feature -p 1 --description "..."
bd close <id> --reason "what was done"
bd remember "key" "value"
```

### AgentDB (semantic vector memory)

Search past patterns and solutions by meaning, not just keywords.

```python
from turboflow_adapter.strands.memory import remember, recall

remember("pattern/retry", "Use exponential backoff with jitter", "pattern")
results = recall("how to handle retries")  # finds by semantic similarity
```

---

## Codebase Intelligence (GitNexus)

Agents can query the codebase knowledge graph for dependencies, call chains, and blast radius.

```bash
npx gitnexus analyze          # Index your repo
npx gitnexus status           # Check index status
```

Agents get GitNexus tools automatically — they can check blast radius before editing shared code.

---

## Deploy to Cloud

TurboFlow deploys to AWS Bedrock AgentCore as a serverless agent. Same capabilities as local — agent types, team recipes, model routing, memory, tools.

### Setup

```bash
# Install AgentCore CLI
npm install -g @aws/agentcore

# Build deployment package
cd infra/agent-runtime
bash build.sh

# Deploy
agentcore deploy --yes
```

### Invoke

```bash
# Set the runtime ARN (from deploy output)
export TURBOFLOW_RUNTIME_ARN="arn:aws:bedrock-agentcore:us-east-1:..."

# Now tf routes to the cloud automatically
tf "Write a fibonacci function"
tf -a reviewer "Review the auth module"
tf --team feature "Add rate limiting"
```

### CI/CD

Deployment is automated via GitHub Actions. Changes to agent code trigger a deploy with smoke test. See `.github/workflows/deploy-agentcore.yml`.

---

## Architecture

```
tf "prompt"
  ↓
  ├── Cloud (TURBOFLOW_RUNTIME_ARN set)
  │     → AgentCore Runtime (Strands agent in microVM)
  │         ├── create_agent() / create_team()
  │         ├── Beads + AgentDB + GitNexus tools
  │         └── Bedrock (Claude, Haiku, Nova)
  │
  └── Local (default)
        → Strands Agent (Python, direct)
            ├── create_agent() / create_team()
            ├── Beads + AgentDB + GitNexus tools
            └── Bedrock / Anthropic API / OpenAI
```

### Backends

| Backend | Type | Use case |
|---|---|---|
| Strands Agents | Programmatic (Python SDK) | Default for local + cloud. Full TurboFlow features. |
| Claude Code | CLI | Interactive terminal coding sessions |
| Kiro CLI | CLI | AWS-native interactive coding |
| Aider | CLI | Multi-model pair programming |
| OpenHands | CLI/Docker | Open-source autonomous agent |

---

## Observability

TurboFlow includes OpenTelemetry integration via Strands and cost tracking:

```python
from turboflow_adapter.strands import setup_telemetry, track_execution

# Enable OTEL tracing
setup_telemetry(console=True)  # dev
setup_telemetry(otlp=True)     # production (CloudWatch, Jaeger)

# Track execution with cost estimation
with track_execution("coder", "implement login", "sonnet") as tracker:
    result = agent("implement login")
    tracker.record_result(result)
print(tracker.metrics.summary())
# [coder] implement login... | 1500ms | 5000 tokens | $0.0225 | ✓
```

---

## Legacy CLI (Ruflo)

The original Ruflo-based CLI still works alongside the new `tf` command:

```bash
rf-swarm              # Ruflo hierarchical swarm
rf-spawn coder        # Spawn a Ruflo agent
rf-doctor             # Ruflo health check
turbo-status          # Full status check
turbo-help            # Command reference
```

See [docs/01-release-notes-v4.md](docs/01-release-notes-v4.md) for the v4.0 Ruflo migration details.

---

## Project Structure

```
turbo-flow/
├── agent-adapter/               ← Agent Adapter (Phase 2)
│   ├── python/                  ← Python adapter + Strands value layer
│   │   ├── turboflow_adapter/   ← Core library
│   │   │   ├── strands/         ← Agent types, teams, tools, memory, observability
│   │   │   └── backends/        ← Claude, Aider, OpenHands, Strands, Kiro
│   │   ├── tests/               ← 71 unit tests
│   │   └── examples/            ← Runnable examples
│   ├── ts/                      ← TypeScript adapter (CLI wrappers)
│   └── shell-integration.sh     ← Shell functions (tf, agent-*)
├── infra/                       ← AWS infrastructure (Phase 3)
│   ├── agent-runtime/           ← AgentCore Runtime entry point
│   └── turboflow_infra/         ← CDK stacks (Platform + Tenant)
├── devpods/                     ← Setup & bootstrapping
│   ├── Taskfile.yml             ← 10-step idempotent setup
│   ├── bootstrap.sh             ← Universal entry point
│   └── templates/               ← CLAUDE.md, aliases, statusline
├── planning/                    ← Product plan, evaluations
├── docs/                        ← User documentation
├── Dockerfile                   ← Pre-baked container image
└── docker-compose.yml           ← Local Docker usage
```

---

## License

MIT — Copyright (c) 2025-2026 Adventure Wave Labs

---

<div align="center">

**Built & Presented by Adventure Wave Labs**

*TurboFlow — Multi-agent AI coding platform. Strands Agents. Amazon Bedrock. Cross-session memory. One command.*

</div>
