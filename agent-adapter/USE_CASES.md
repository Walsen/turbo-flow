# Agent Adapter — Use Cases & Examples

All commands run from `agent-adapter/python/`. Set Bedrock env first:

```bash
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=us-east-1
```

---

## 1. Pre-configured agent types

Create agents with tuned system prompts, default model tiers, and TurboFlow tools (Beads, file ops) built in.

```python
from turboflow_adapter.strands import create_agent

# Coder agent — Sonnet, has file tools + Beads
coder = create_agent("coder")
result = coder("Write a Python function to merge two sorted lists efficiently")

# Reviewer agent — Sonnet, has Beads + file read (no write)
reviewer = create_agent("reviewer")
result = reviewer("Review the code in src/auth.py for security issues")

# Architect agent — Opus (auto), has Beads + file read
architect = create_agent("system-architect")
result = architect("Design an event-driven architecture for order processing")

# Security agent — Opus (auto), cites CWE IDs
security = create_agent("security-architect")
result = security("Audit the authentication flow in this project")
```

Available types: `coder`, `tester`, `reviewer`, `system-architect`, `researcher`, `coordinator`, `security-architect`

---

## 2. Automatic model routing

Let TurboFlow pick the right model tier based on task complexity — saves ~75% on API costs.

```python
from turboflow_adapter.strands import create_agent, select_tier

tasks = [
    "Fix typo in README",                          # → haiku
    "Implement JWT token refresh",                  # → sonnet
    "Design a CQRS architecture with event sourcing for distributed transactions",  # → opus
]

for task in tasks:
    tier = select_tier(task)
    print(f"{tier.value}: {task[:50]}")
    agent = create_agent("coder", model_tier=tier)
    result = agent(task)
```

---

## 3. Multi-agent teams (replaces rf-swarm)

Pre-built team recipes using the supervisor-agent pattern. The supervisor delegates to specialist agents.

```python
from turboflow_adapter.strands import create_team

# Feature team: architect + coder + tester + reviewer
team = create_team("feature")
result = team("Implement a rate limiter middleware for the Express API")

# Bug fix team: researcher + coder + tester
team = create_team("bug-fix")
result = team("Users report 500 errors when uploading files larger than 10MB")

# Code review team: reviewer + security architect
team = create_team("code-review")
result = team("Review the PR that adds OAuth2 integration")

# Security audit team: security architect + researcher + reviewer
team = create_team("security-audit")
result = team("Audit the payment processing module for vulnerabilities")
```

---

## 4. Beads integration (cross-session memory)

Agents automatically check Beads at session start and record work when done.

```python
from turboflow_adapter.strands import create_agent

# The coder agent's system prompt tells it to check Beads first
coder = create_agent("coder")

# This agent will:
# 1. Call beads_ready to check project state
# 2. Do the work
# 3. Create Beads issues for what was done
result = coder("Implement the user registration endpoint based on open tasks")
```

Or use Beads tools directly:

```python
from turboflow_adapter.strands.tools import beads_ready, beads_create, beads_remember

# Check project state
print(beads_ready())

# Create a task
beads_create("Add rate limiting", type="feature", priority=2, description="Add rate limiting to all API endpoints")

# Store a lesson learned
beads_remember("lesson/rate-limiting", "Use sliding window algorithm, not fixed window — handles burst traffic better")
```

---

## 5. Custom agent with extra tools

Add your own tools alongside TurboFlow defaults.

```python
from strands import tool
from turboflow_adapter.strands import create_agent

@tool(name="run_tests", description="Run the project's test suite and return results.")
def run_tests() -> str:
    import subprocess
    result = subprocess.run(["npm", "test"], capture_output=True, text=True, timeout=120)
    return result.stdout + result.stderr

# Coder agent with test runner added
coder = create_agent("coder", extra_tools=[run_tests])
result = coder("Fix the failing test in auth.test.ts and verify all tests pass")
```

---

## 6. Model tier override

Force a specific model regardless of agent type defaults.

```python
from turboflow_adapter.strands import create_agent

# Use Haiku for a quick task (cheapest)
agent = create_agent("coder", model_tier="haiku")
result = agent("Add a docstring to the fibonacci function")

# Use Opus for a complex task (most capable)
agent = create_agent("coder", model_tier="opus")
result = agent("Refactor the entire auth module to use the Strategy pattern")
```

---

## 7. CLI usage

The adapter CLI still works for quick one-off tasks.

```bash
# Run via Strands backend
uv run tf-adapter exec --backend strands --model sonnet "List the Python files in this project"

# Check all backends
uv run tf-adapter status

# Health check
uv run tf-adapter health --backend strands

# Model resolution
uv run tf-adapter resolve-model opus --backend strands
```

---

## 8. Direct model creation

Use the model factory directly when you need full control.

```python
from turboflow_adapter.strands.models import create_model, ModelTier

# Create a Bedrock model (auto-detects from env)
model = create_model(ModelTier.SONNET)

# Use it with a raw Strands agent
from strands import Agent
agent = Agent(model=model, system_prompt="You are a helpful assistant.")
result = agent("Hello!")
```

---

## What TurboFlow adds vs raw Strands

| You want to... | Raw Strands | TurboFlow Strands |
|---|---|---|
| Create a coding agent | Write system prompt, pick model, add tools manually | `create_agent("coder")` — prompt, model, tools pre-configured |
| Pick the right model | You decide every time | `select_tier(task)` — auto-selects based on complexity |
| Run a feature team | Build supervisor + specialists from scratch | `create_team("feature")` — one line |
| Use cross-session memory | Not available | Beads tools built into every agent |
| Read/write project files | Write your own tools | `file_tools()` included by default |
| Track work and decisions | Manual | Agents auto-check and update Beads |
