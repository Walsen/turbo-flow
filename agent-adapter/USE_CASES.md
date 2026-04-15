# TurboFlow Use Cases & Examples

Set Bedrock env first:

```bash
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=us-east-1
```

Python examples run from `agent-adapter/python/`.

---

## Day-to-Day Development

### Start a coding session

Check project state, pick up where you left off.

```python
from turboflow_adapter.strands import create_agent
from turboflow_adapter.strands.tools import beads_ready

# Check what's open
print(beads_ready())

# Pick up work — the coder agent reads Beads automatically
coder = create_agent("coder")
result = coder("Pick up the highest-priority open task and implement it")
```

### Implement a feature

Single agent for straightforward features.

```python
from turboflow_adapter.strands import create_agent

coder = create_agent("coder")
result = coder("""
Implement a REST endpoint POST /api/users/register that:
- Accepts email, password, name
- Validates email format and password strength
- Hashes password with bcrypt
- Stores in the users table
- Returns 201 with user ID (no password in response)
- Returns 409 if email already exists
""")
```

### Implement a complex feature with a team

Multi-agent team for features that need design, implementation, tests, and review.

```python
from turboflow_adapter.strands import create_team

team = create_team("feature")
result = team("""
Implement rate limiting for the API:
- Sliding window algorithm (not fixed window)
- Per-user limits: 100 requests/minute for free tier, 1000 for pro
- Redis-backed counter with TTL
- Return 429 with Retry-After header when exceeded
- Add middleware that applies to all routes
- Include unit tests and integration tests
""")
```

### Fix a bug

The bug-fix team investigates, fixes, and writes a regression test.

```python
from turboflow_adapter.strands import create_team

team = create_team("bug-fix")
result = team("""
Bug report: Users get 500 errors when uploading files larger than 10MB.
Stack trace shows: PayloadTooLargeError in express body-parser.
Expected: files up to 50MB should work. Over 50MB should return 413.
""")
```

### Quick fix — use Haiku to save costs

For trivial changes, use the cheapest model.

```python
from turboflow_adapter.strands import create_agent

agent = create_agent("coder", model_tier="haiku")
result = agent("Fix the typo in README.md line 42: 'recieve' should be 'receive'")
```

### Let TurboFlow pick the model automatically

```python
from turboflow_adapter.strands import create_agent, select_tier

tasks = [
    "Fix typo in README",                                    # → haiku ($)
    "Add input validation to the registration endpoint",     # → sonnet ($$)
    "Design a CQRS event-sourcing architecture for orders",  # → opus ($$$)
]

for task in tasks:
    tier = select_tier(task)
    print(f"  {tier.value}: {task[:60]}")
    agent = create_agent("coder", model_tier=tier)
    result = agent(task)
```

---

## Code Quality & Review

### Review a file or module

```python
from turboflow_adapter.strands import create_agent

reviewer = create_agent("reviewer")
result = reviewer("Review src/auth/middleware.ts for correctness, security, and maintainability")
```

### Review a PR (multi-agent)

Reviewer checks code quality, security architect checks vulnerabilities.

```python
from turboflow_adapter.strands import create_team

team = create_team("code-review")
result = team("""
Review the changes in the current branch compared to main.
Focus on:
- The new OAuth2 integration in src/auth/
- The database migration in migrations/
- Any new API endpoints
""")
```

### Security audit

```python
from turboflow_adapter.strands import create_team

team = create_team("security-audit")
result = team("""
Audit the payment processing module:
- Check for injection vulnerabilities (SQL, NoSQL, command)
- Verify authentication and authorization on all endpoints
- Check for sensitive data exposure in logs or responses
- Review third-party dependencies for known CVEs
- Check CORS and CSP headers
""")
```

---

## Architecture & Design

### Build an entire application (design → code → QE)

One line — the supervisor coordinates architect, coder, tester, reviewer, and security architect across three phases.

```python
from turboflow_adapter.strands import create_team

team = create_team("full-build")
result = team("""
Build a task management API:
- CRUD for projects and tasks
- User assignment and due dates
- Status workflow (todo → in_progress → review → done)
- REST API with OpenAPI spec
- PostgreSQL with Prisma ORM
- TypeScript / Express
- JWT authentication
""")
```

The supervisor runs:
1. **Design** — architect produces component diagram, DB schema, API contract, file structure
2. **Build** — coder implements the design, tester writes unit + integration tests
3. **QE gate** — reviewer checks code quality, security architect audits for OWASP Top 10
4. **Report** — synthesized summary with findings by severity and remaining work

All decisions and findings are recorded in Beads automatically.

### Design a system

```python
from turboflow_adapter.strands import create_agent

architect = create_agent("system-architect")
result = architect("""
Design a notification system for our SaaS platform:
- Support email, SMS, push, and in-app notifications
- Users can configure preferences per channel
- Must handle 10K notifications/minute at peak
- Need delivery tracking and retry logic
- Must be extensible for new channels
Provide: component diagram, data model, API contracts, and trade-off analysis.
""")
```

### Evaluate a technical decision

```python
from turboflow_adapter.strands import create_agent

architect = create_agent("system-architect")
result = architect("""
We need to choose between:
A) PostgreSQL with row-level security for multi-tenancy
B) Separate database per tenant
C) Shared database with tenant_id column

Context: 50-200 tenants, 10GB-100GB per tenant, need strong isolation for enterprise clients.
Evaluate each option on: isolation, cost, operational complexity, performance, and migration difficulty.
""")
```

---

## Testing

### Generate tests for existing code

```python
from turboflow_adapter.strands import create_agent

tester = create_agent("tester")
result = tester("""
Write comprehensive tests for src/services/payment.ts:
- Unit tests for each public method
- Edge cases: invalid amounts, expired cards, network timeouts
- Integration test with Stripe test API
- Use the existing Jest setup
""")
```

### Investigate a flaky test

```python
from turboflow_adapter.strands import create_agent

researcher = create_agent("researcher")
result = researcher("""
The test 'should process concurrent payments' in tests/payment.test.ts
fails intermittently (~20% of runs). Investigate:
- Check for race conditions
- Check for shared state between tests
- Check for timing-dependent assertions
- Suggest a fix
""")
```

---

## Research & Investigation

### Investigate a production issue

```python
from turboflow_adapter.strands import create_agent

researcher = create_agent("researcher")
result = researcher("""
Production alert: API response times spiked from 200ms to 2s at 14:30 UTC.
- Check recent deployments
- Look at database query patterns
- Check for N+1 queries or missing indexes
- Review connection pool settings
- Provide root cause analysis and remediation steps
""")
```

### Analyze a codebase before making changes

```python
from turboflow_adapter.strands import create_agent

researcher = create_agent("researcher")
result = researcher("""
I need to add WebSocket support to the API. Before I start:
- Map out the current request handling architecture
- Identify where WebSocket connections should be managed
- List files that will need changes
- Flag any potential conflicts with existing middleware
""")
```

---

## Project Memory (Beads)

### Track decisions and lessons

```python
from turboflow_adapter.strands.tools import beads_create, beads_remember

# Record an architectural decision
beads_create(
    "Use Redis for rate limiting",
    type="decision",
    priority=0,
    description="Chose Redis over in-memory counters. Reasons: works across multiple server instances, built-in TTL, atomic operations. Trade-off: adds Redis as a dependency."
)

# Store a lesson learned
beads_remember(
    "lesson/rate-limiting",
    "Use sliding window algorithm, not fixed window — handles burst traffic better and is fairer to users"
)

# Store a pattern that worked
beads_remember(
    "pattern/error-handling",
    "Always return structured error responses: { error: string, code: string, details?: object }. Clients depend on this format."
)
```

### Start a session with full context

```python
from turboflow_adapter.strands import create_agent
from turboflow_adapter.strands.tools import beads_ready

# See everything: open tasks, blockers, recent decisions
state = beads_ready()
print(state)

# Agent picks up context automatically
coder = create_agent("coder")
result = coder("Continue working on the highest priority open task. Check Beads for context first.")
```

---

## Custom Agents & Tools

### Add project-specific tools

```python
from strands import tool
from turboflow_adapter.strands import create_agent

@tool(name="run_tests", description="Run the project test suite.")
def run_tests(path: str = "") -> str:
    import subprocess
    cmd = ["npm", "test"]
    if path:
        cmd.extend(["--", path])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return result.stdout + result.stderr

@tool(name="check_types", description="Run TypeScript type checker.")
def check_types() -> str:
    import subprocess
    result = subprocess.run(["npx", "tsc", "--noEmit"], capture_output=True, text=True, timeout=60)
    return result.stdout + result.stderr

# Coder with project-specific quality tools
coder = create_agent("coder", extra_tools=[run_tests, check_types])
result = coder("Implement the user profile update endpoint. Run tests and type check when done.")
```

### Override the system prompt

```python
from turboflow_adapter.strands import create_agent

# Agent specialized for your stack
agent = create_agent(
    "coder",
    system_prompt_override="""
    You are a senior TypeScript developer working on a Next.js 14 + Prisma + PostgreSQL stack.
    Follow these conventions:
    - Use server actions for mutations
    - Use Zod for all input validation
    - Use Prisma for all database access (never raw SQL)
    - Error responses follow { error: string, code: string } format
    - All new code must have tests
    Check Beads for project context before starting.
    """
)
result = agent("Add a PATCH /api/users/:id endpoint for profile updates")
```

---

## CLI Quick Reference

```bash
# Run a prompt via Strands
uv run tf-adapter exec --backend strands --model sonnet "Implement login endpoint"

# Use Haiku for cheap tasks
uv run tf-adapter exec --backend strands --model haiku "Fix typo in README"

# Target specific files
uv run tf-adapter exec --backend strands -f src/auth.ts -f src/middleware.ts "Add JWT refresh"

# Custom system prompt
uv run tf-adapter exec --backend strands -s "You are a security auditor. Cite CWE IDs." "Review auth module"

# Check status
uv run tf-adapter status
uv run tf-adapter health --backend strands
uv run tf-adapter resolve-model opus --backend strands

# Use Claude Code CLI (interactive terminal)
uv run tf-adapter exec --backend claude "Start an interactive coding session"
```

---

## What TurboFlow adds vs raw Strands

| You want to... | Raw Strands | TurboFlow |
|---|---|---|
| Create a coding agent | Write prompt, pick model, add tools | `create_agent("coder")` |
| Pick the right model | You decide every time | `select_tier(task)` auto-selects |
| Run a feature team | Build supervisor + specialists | `create_team("feature")` |
| Track work across sessions | Not available | Beads built into every agent |
| Read/write project files | Write your own tools | Included by default |
| Record decisions | Manual | Agents auto-update Beads |
| Interactive terminal | Not available | Switch to Claude Code backend |
