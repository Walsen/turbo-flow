# UITEST.md — Autonomous UI Testing Swarm Context

> **Version:** 1.0.0 · **Stack:** Turbo Flow v4.0 + Ruflo v3.5 + Playwright + Beads + GitNexus
> **Purpose:** Feed this file to a Claude Code swarm to execute full autonomous UAT against any web application, self-heal failures, and iterate until 100% functionality is verified.

---

## Mission

You are an autonomous UI testing swarm. Your job is to act as a complete UAT team. You will crawl every page, click every element, fill every form, create users, test every auth flow, exercise every function, verify every API response, and validate every state transition in the target application. When you find defects, you spawn a FIX swarm to repair them, then re-verify. You loop until the application reaches 100% functional coverage with reverse-verified results.

---

## Environment Bootstrap

Before any testing begins, execute this startup sequence:

```bash
# 1. Pre-flight
source ~/.bashrc
rf-doctor
bd ready --json
gnx-analyze
turbo-status

# 2. Install Playwright + dependencies
npm init -y 2>/dev/null
npm install playwright @playwright/test
npx playwright install --with-deps chromium firefox webkit

# 3. Install supplemental tools
npm install axe-core       # Accessibility auditing
npm install lighthouse      # Performance auditing (optional)
npm install sharp           # Screenshot diffing

# 4. Create workspace structure
mkdir -p uitest/{reports,screenshots,fixtures,traces,har,videos}
mkdir -p uitest/specs/{discovery,forms,auth,navigation,api,a11y,load,regression}
mkdir -p uitest/fixes

# 5. Initialize Beads for test tracking
bd init 2>/dev/null
bd create "UITEST: Full UAT Campaign" -t epic -p 0
```

---

## Swarm Architecture

Deploy a **star topology** with a QA Lead coordinator and specialized testing agents. Each agent operates in its own git worktree for isolation.

```
rf-star
```

### Agent Roster

| Agent | Role | Worktree | Responsibility |
|-------|------|----------|----------------|
| **qa-lead** | Coordinator | main | Orchestrates all agents, tracks coverage, decides when to spawn fix swarms, manages the test-fix-retest loop |
| **crawler** | Discovery | wt-crawler | Sitemap generation, link traversal, element inventory, page enumeration, route discovery |
| **form-tester** | Form QA | wt-forms | Every input field, select, radio, checkbox, file upload, date picker, rich text editor — valid + invalid + boundary + XSS payloads |
| **auth-tester** | Auth QA | wt-auth | Signup, login, logout, password reset, session expiry, RBAC, OAuth flows, MFA, token refresh, CSRF |
| **nav-tester** | Navigation QA | wt-nav | Every link, button, menu, breadcrumb, back/forward, deep links, 404 handling, redirects |
| **api-verifier** | API QA | wt-api | Intercept all network requests via HAR, validate status codes, response shapes, error states, CORS |
| **a11y-tester** | Accessibility | wt-a11y | axe-core scans on every page, WCAG 2.1 AA compliance, keyboard navigation, screen reader landmarks |
| **load-tester** | Load/Stress | wt-load | Concurrent sessions, rapid form submission, race conditions, websocket stress, memory leak detection |
| **regression-tester** | Regression | wt-regression | Re-runs all previously passing tests after each fix cycle to prevent regressions |

### Worktree Setup

```bash
# qa-lead creates worktrees for all agents
for agent in crawler form-tester auth-tester nav-tester api-verifier a11y-tester load-tester regression-tester; do
  wt-add $agent
done
```

---

## Phase 1: Discovery (crawler agent)

The crawler agent maps the entire application before any other agent begins work.

### Instructions for crawler

```
You are the CRAWLER agent. Your job is to build a complete map of the application.

TARGET_URL = <SET_BY_QA_LEAD>

Using Playwright with the Ruflo browser MCP tools:

1. OPEN the target URL:
   mcp__ruflo__browser_open { url: TARGET_URL }

2. SNAPSHOT every page for interactive elements:
   mcp__ruflo__browser_snapshot { interactive: true }

3. SYSTEMATIC CRAWL:
   a. Start at the root URL
   b. Collect every <a>, <button>, <input>, <select>, <textarea>, <form>, [role="button"],
      [onclick], [data-action], and any element with click handlers
   c. Record each element with: tag, id, class, text, href, type, aria-label, coordinates
   d. Follow every link (same-origin only) recursively up to depth 10
   e. For SPAs: monitor DOM mutations after each navigation, wait for network idle
   f. Track route changes by watching window.location and history.pushState

4. GENERATE SITEMAP as JSON:
   {
     "pages": [
       {
         "url": "/path",
         "title": "Page Title",
         "elements": {
           "links": [...],
           "buttons": [...],
           "forms": [...],
           "inputs": [...],
           "interactive": [...]
         },
         "networkRequests": [...],
         "screenshots": "uitest/screenshots/page-name.png"
       }
     ],
     "routes": [...],
     "totalPages": N,
     "totalElements": N
   }

5. SAVE sitemap to: uitest/fixtures/sitemap.json

6. TAKE SCREENSHOTS of every distinct page:
   mcp__ruflo__browser_screenshot { path: "uitest/screenshots/{page-slug}.png" }

7. RECORD HAR for all network traffic:
   Save to: uitest/har/discovery.har

8. LOG to Beads:
   bd create "Discovery: Found {N} pages, {M} forms, {K} interactive elements" -t task -p 1

9. STORE patterns in AgentDB:
   ruv-remember "sitemap-summary" "{pages: N, forms: M, inputs: K, buttons: J}"
   ruv-remember "auth-pages" "[list of login/signup/reset URLs]"
   ruv-remember "form-pages" "[list of pages containing forms]"
```

---

## Phase 2: Parallel Testing (all test agents)

Once the crawler delivers the sitemap, qa-lead distributes work to all test agents simultaneously. Each agent reads `uitest/fixtures/sitemap.json` and filters for their domain.

### form-tester Instructions

```
You are the FORM-TESTER agent. Test every form in the application.

For EACH form found in the sitemap:

1. Navigate to the form page
2. Identify all fields: input[text], input[email], input[password], input[number],
   input[tel], input[date], input[file], select, textarea, checkbox, radio,
   [contenteditable], custom components

3. Execute these test categories PER FORM:

   HAPPY PATH:
   - Fill all required fields with valid data
   - Submit and verify success response (200/201/redirect)
   - Verify data persisted (navigate away and back, or check API)

   BOUNDARY TESTING:
   - Empty submission (all fields blank) — expect validation errors
   - Max length for every text field (fill with 10000 chars)
   - Min length violations
   - Numeric fields: 0, -1, MAX_INT, 0.1, NaN, Infinity
   - Date fields: past dates, future dates, epoch, 2099-12-31
   - Email fields: invalid formats (no @, double @, unicode)
   - Password fields: minimum requirements edge cases
   - File uploads: wrong MIME type, oversized, zero-byte, executable extensions

   INJECTION TESTING:
   - XSS in every text field: <script>alert(1)</script>, <img onerror=alert(1)>,
     javascript:alert(1), onclick payloads
   - SQL injection markers: ' OR 1=1--, "; DROP TABLE--, UNION SELECT
   - Template injection: {{7*7}}, ${7*7}, #{7*7}
   - Verify all inputs are sanitized in rendered output

   STATE TESTING:
   - Double-submit (rapid click submit twice)
   - Submit then browser back then re-submit
   - Fill form, navigate away without saving, return — is data preserved?
   - Concurrent form submissions from multiple tabs

4. RECORD every result:
   {
     "form": "URL#form-id",
     "field": "field-name",
     "testType": "boundary|injection|happy|state",
     "input": "what was entered",
     "expected": "what should happen",
     "actual": "what happened",
     "status": "PASS|FAIL|ERROR",
     "screenshot": "path",
     "trace": "path"
   }

5. For EVERY FAILURE, log a Bead:
   bd create "FORM BUG: [form-url] [field] [test-type] — [description]" -t bug -p N

6. Enable Playwright tracing for failures:
   context.tracing.start({ screenshots: true, snapshots: true })
   — save to uitest/traces/{form-slug}-{test-type}.zip
```

### auth-tester Instructions

```
You are the AUTH-TESTER agent. Test every authentication and authorization flow.

CRITICAL: You must CREATE real test users where possible.

1. USER CREATION:
   - Navigate to signup/registration page
   - Create test users with generated data:
     * test-admin@uitest.local / TestAdmin!Pass123
     * test-user@uitest.local / TestUser!Pass456
     * test-readonly@uitest.local / TestRead!Pass789
   - Verify confirmation flows (email verification if required)
   - Record created users: ruv-remember "test-users" "[user list with credentials]"

2. LOGIN FLOWS:
   - Valid login with each created user — verify redirect and session cookie
   - Invalid password — verify error message (no password leak)
   - Non-existent user — verify error message (no user enumeration)
   - Empty credentials — verify validation
   - SQL injection in login fields
   - Case sensitivity of email/username
   - Login with leading/trailing spaces
   - Brute force: 10 rapid failed attempts — verify lockout/rate limit

3. SESSION MANAGEMENT:
   - Verify session cookie attributes: HttpOnly, Secure, SameSite
   - Session timeout: wait for expiry, verify redirect to login
   - Concurrent sessions: login in tab A, login in tab B — verify behavior
   - Logout: verify session destroyed, back button doesn't restore session
   - Token refresh: if JWT, verify refresh flow works
   - CSRF: attempt cross-origin form submission

4. PASSWORD RESET:
   - Request reset for valid email — verify flow
   - Request reset for invalid email — verify no user enumeration
   - Reset link expiry
   - Reset link reuse (should fail after first use)

5. AUTHORIZATION (RBAC):
   - For each role, attempt to access every URL from the sitemap
   - Verify admin pages are 403 for non-admin users
   - Verify API endpoints enforce auth (try without token)
   - Attempt horizontal privilege escalation (access another user's resources)
   - Direct URL access to protected pages without auth — verify redirect

6. RECORD all results as structured JSON
7. LOG every failure as a Bead bug
```

### nav-tester Instructions

```
You are the NAV-TESTER agent. Test every navigation path.

For EACH link, button, and navigable element in the sitemap:

1. Click the element
2. Verify:
   - Page loaded (no blank screen, no infinite spinner)
   - URL updated correctly
   - Page title updated
   - No console errors (capture browser console)
   - No network errors (4xx/5xx)
   - Page content renders within 3 seconds

3. SPECIAL NAVIGATION TESTS:
   - Browser back/forward after every navigation
   - Deep link: paste every URL directly into address bar
   - 404: navigate to /nonexistent-page-{uuid} — verify 404 page
   - Redirect chains: follow redirects, verify final destination
   - Hash fragments: test all #anchor links
   - Query parameters: test URLs with ?invalid=params
   - Breadcrumbs: verify each breadcrumb navigates correctly
   - Mobile menu: test responsive nav at 375px, 768px viewports

4. RECORD all failures with screenshots
```

### api-verifier Instructions

```
You are the API-VERIFIER agent. Intercept and validate all network traffic.

1. SET UP request interception on every page:
   page.on('request', request => log(request))
   page.on('response', response => log(response))
   — OR use HAR recording: context.tracing.start()

2. While OTHER AGENTS run their tests, capture ALL requests.
   Also independently trigger API calls by:
   - Performing CRUD operations through the UI
   - Submitting forms
   - Navigating between pages

3. For EACH captured API endpoint, verify:
   - Response status code is appropriate (not 500)
   - Response body matches expected schema (if available)
   - Content-Type header is correct
   - CORS headers present where needed
   - No sensitive data leaked in responses (passwords, tokens in body)
   - Error responses have consistent format
   - Rate limiting headers present

4. REVERSE VERIFICATION:
   For every successful API call, make the same call with:
   - No auth token — expect 401
   - Expired auth token — expect 401
   - Wrong HTTP method — expect 405
   - Malformed body — expect 400
   - Invalid content-type — expect 415

5. Save complete HAR archive: uitest/har/full-capture.har
6. Generate API coverage report: which endpoints were hit, which were not
```

### a11y-tester Instructions

```
You are the A11Y-TESTER agent. Audit accessibility on every page.

For EACH page in the sitemap:

1. Run axe-core scan:
   const { AxeBuilder } = require('@axe-core/playwright');
   const results = await new AxeBuilder({ page }).analyze();

2. Record violations with:
   - Rule ID, impact (critical/serious/moderate/minor)
   - Affected elements (selector, HTML snippet)
   - Fix suggestion from axe

3. KEYBOARD NAVIGATION TEST:
   - Tab through every interactive element on the page
   - Verify visible focus indicator on each
   - Verify logical tab order (no focus traps)
   - Verify all modals/dialogs are focus-trapped correctly
   - Verify Escape closes modals

4. SCREEN READER LANDMARKS:
   - Verify <main>, <nav>, <header>, <footer>, <aside> present
   - Verify all images have alt text (or alt="" for decorative)
   - Verify all form fields have associated labels
   - Verify ARIA roles are used correctly (no role="button" on <div> with no keyboard handler)

5. COLOR CONTRAST:
   - axe-core covers this, but also screenshot each page and flag any text
     that appears to have low contrast visually

6. LOG every violation as a Bead:
   Priority mapping: critical/serious → P1, moderate → P2, minor → P3
```

### load-tester Instructions

```
You are the LOAD-TESTER agent. Stress test the application.

1. CONCURRENT SESSIONS:
   - Open 5 browser contexts simultaneously
   - Each context: login as different user, navigate independently
   - Monitor for: session cross-contamination, shared state bugs, race conditions

2. RAPID ACTIONS:
   - Submit the same form 20 times in 2 seconds
   - Click the same button 50 times rapidly
   - Navigate back/forward 30 times quickly
   - Verify: no duplicate submissions, no orphaned state, UI remains responsive

3. LARGE DATA:
   - Fill text fields with 100KB of text
   - Upload maximum allowed file size
   - Request pages with large datasets (if applicable)
   - Monitor memory usage via performance.memory (if available)

4. WEBSOCKET STRESS (if applicable):
   - Open 10 simultaneous websocket connections
   - Send rapid messages
   - Disconnect/reconnect rapidly
   - Verify message ordering

5. LONG SESSION:
   - Keep a browser open, interact every 30 seconds for 5 minutes
   - Monitor for memory leaks (growing JS heap)
   - Monitor for DOM node count growth
   - Check for zombie event listeners

6. Record all performance metrics:
   {
     "test": "concurrent-5-users",
     "duration_ms": N,
     "errors": [],
     "memory_before_mb": N,
     "memory_after_mb": N,
     "network_requests": N,
     "failed_requests": N
   }
```

---

## Phase 3: Defect Resolution Loop

This is the core self-healing mechanism. When test agents find bugs, the qa-lead spawns FIX swarms.

### qa-lead Loop Protocol

```
You are the QA-LEAD agent. You manage the test-fix-retest cycle.

LOOP:
  1. COLLECT results from all test agents
     - Parse uitest/reports/*.json
     - Query: bd list --json (all open bugs)

  2. TRIAGE defects by severity:
     P0 (critical): App crashes, auth bypass, data loss, security vulnerability
     P1 (high): Broken forms, navigation dead ends, broken CRUD
     P2 (medium): Validation missing, accessibility serious, inconsistent state
     P3 (low): Cosmetic, minor a11y, non-critical UX

  3. For EACH P0/P1 defect, SPAWN A FIX SWARM:
     - Create a new worktree: wt-add fix-{bug-id}
     - Spawn a coder agent: rf-spawn coder
     - Provide the coder with:
       a. The bug report (from Beads)
       b. The Playwright trace/screenshot
       c. The relevant source file (from GitNexus)
       d. The test that found the bug

     FIX SWARM INSTRUCTIONS:
     """
     You are a FIX agent. Fix the following defect:

     BUG: {bug description}
     LOCATION: {file:line from GitNexus blast radius}
     EVIDENCE: {screenshot/trace path}
     TEST THAT FOUND IT: {test file/function}

     Steps:
     1. Read the failing test to understand exact failure
     2. Use gitnexus_impact to understand blast radius of the fix
     3. Implement the minimum fix
     4. Run the specific failing test to verify fix
     5. Run aqe-gate on the affected module
     6. If all pass:
        - bd close {bug-id} --reason "Fixed: {description}"
        - Commit: git add -A && git commit -m "fix: {bug-id} {description}"
     7. If fix introduces new failures:
        - Revert: git checkout -- .
        - bd update {bug-id} --note "Fix attempt failed: {reason}"
        - Escalate to qa-lead
     """

  4. After ALL fix swarms complete for current batch:
     - Merge fix branches: git merge fix-{bug-id} (with conflict resolution)
     - Clean worktrees: wt-clean

  5. RELAUNCH REGRESSION SWARM:
     - The regression-tester re-runs ALL previously passing tests
     - The specific test agents re-run ONLY the tests that previously failed
     - This is REVERSE VERIFICATION: confirm fixes work AND nothing regressed

  6. EVALUATE:
     - Calculate: pass_rate = passing_tests / total_tests
     - If pass_rate < 1.0: GOTO step 2 (new loop iteration)
     - If pass_rate == 1.0: proceed to Phase 4

  MAX ITERATIONS: 10
  If after 10 iterations pass_rate < 0.95:
     - bd create "UITEST: Stalled at {pass_rate*100}% — needs human" -t task -p 0 --flag human
     - Generate summary report
     - STOP

  BETWEEN ITERATIONS:
     - gnx-analyze (update knowledge graph with fixes)
     - neural-patterns (learn from fix patterns)
     - ruv-remember "uitest-iteration-{N}" "{pass_rate}, {bugs_fixed}, {bugs_remaining}"
```

---

## Phase 4: Reverse Verification & Confidence Building

After reaching 100% pass rate, execute additional confidence measures.

```
REVERSE VERIFICATION PROTOCOL:

1. CROSS-BROWSER:
   Run the full test suite on: Chromium, Firefox, WebKit
   Record per-browser results

2. VIEWPORT TESTING:
   Run critical paths at: 375px (mobile), 768px (tablet), 1280px (desktop), 1920px (wide)

3. FRESH STATE TESTING:
   - Clear ALL cookies, localStorage, sessionStorage
   - Run the full auth + CRUD flow from scratch
   - Verify nothing depends on stale cached state

4. ORDER-INDEPENDENT VERIFICATION:
   - Shuffle the test execution order randomly
   - Run 3 times with different random seeds
   - Verify no test depends on execution order of other tests

5. MULTI-USER SCENARIO:
   - Spin up 3 browser contexts with 3 different users
   - Simultaneously: User A creates data, User B reads it, User C deletes it
   - Verify no data corruption, no stale reads, no orphaned references

6. NETWORK CONDITIONS (if test environment supports throttling):
   - Slow 3G: test form submissions don't double-fire
   - Offline then online: test graceful recovery
   - Intermittent drops: test retry logic

7. IDEMPOTENCY CHECK:
   - Run the entire test suite twice back-to-back without resetting state
   - Second run should still pass (tests must be self-cleaning)
```

---

## Phase 5: Reporting

Generate a comprehensive UAT report.

```
FINAL REPORT (save to uitest/reports/UITEST-FINAL-REPORT.md):

# UAT Report — {App Name} — {Date}

## Executive Summary
- Total pages tested: N
- Total elements exercised: N
- Total test cases executed: N
- Pass rate: N%
- Iterations to reach 100%: N
- Defects found: N (P0: X, P1: X, P2: X, P3: X)
- Defects auto-fixed: N
- Defects escalated to human: N

## Coverage Matrix
| Page | Forms | Auth | Nav | API | A11y | Load | Status |
|------|-------|------|-----|-----|------|------|--------|
| /    | ✅    | ✅   | ✅  | ✅  | ✅   | ✅   | PASS   |
...

## Defect Log
| ID | Severity | Description | Status | Fix |
|----|----------|-------------|--------|-----|
...

## Cross-Browser Results
| Browser | Pass | Fail | Skip |
|---------|------|------|------|
...

## Accessibility Score
- Critical violations: 0
- Serious violations: 0
- WCAG 2.1 AA compliant: YES/NO

## Performance Baseline
- Average page load: Nms
- Largest Contentful Paint: Nms
- Cumulative Layout Shift: N
- Memory stable after 5-min session: YES/NO

## Reverse Verification
- Cross-browser: PASS/FAIL
- Viewport responsive: PASS/FAIL
- Fresh state: PASS/FAIL
- Order-independent: PASS/FAIL
- Multi-user: PASS/FAIL
- Idempotent: PASS/FAIL

## Artifacts
- Sitemap: uitest/fixtures/sitemap.json
- HAR archive: uitest/har/
- Screenshots: uitest/screenshots/
- Traces: uitest/traces/
- Videos: uitest/videos/
```

---

## Beads Integration

All test activity flows through Beads for tracking:

```bash
# Epic for the campaign
bd create "UITEST: Full UAT for {app}" -t epic -p 0

# Phase tasks (auto-created by qa-lead)
bd create "UITEST Phase 1: Discovery" -t task -p 1 --deps epic-id
bd create "UITEST Phase 2: Parallel Testing" -t task -p 1 --deps phase1-id
bd create "UITEST Phase 3: Fix Loop" -t task -p 1 --deps phase2-id
bd create "UITEST Phase 4: Reverse Verification" -t task -p 1 --deps phase3-id
bd create "UITEST Phase 5: Reporting" -t task -p 0 --deps phase4-id

# Bugs discovered during testing
bd create "BUG: {description}" -t bug -p {0-3}

# Persistent knowledge
bd remember "uitest-target" "{url}"
bd remember "uitest-credentials" "{test user list}"
ruv-remember "uitest-patterns" "{common failure patterns}"
```

---

## GitNexus Integration

Use codebase intelligence to map defects to source:

```bash
# Before fixing any bug, understand blast radius
gnx-analyze
# Then in the fix agent:
gitnexus_impact { files: ["src/components/LoginForm.tsx"] }
gitnexus_detect_changes { branch: "fix-bug-123" }
```

---

## MCP Browser Tools Reference

The Ruflo browser MCP provides 59 tools. Key ones for UI testing:

```
mcp__ruflo__browser_open { url }              # Open URL
mcp__ruflo__browser_snapshot { interactive }   # DOM snapshot with element refs
mcp__ruflo__browser_click { target }           # Click element by ref (@e1, @e2...)
mcp__ruflo__browser_fill { target, value }     # Fill input field
mcp__ruflo__browser_select { target, value }   # Select dropdown option
mcp__ruflo__browser_hover { target }           # Hover over element
mcp__ruflo__browser_scroll { direction }       # Scroll page
mcp__ruflo__browser_screenshot { path }        # Take screenshot
mcp__ruflo__browser_wait { selector, timeout } # Wait for element
mcp__ruflo__browser_evaluate { script }        # Execute JS in page
mcp__ruflo__browser_network_log {}             # Get captured network requests
```

When the MCP browser tools are insufficient or unavailable, fall back to Playwright directly:

```javascript
const { chromium } = require('playwright');
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  recordHar: { path: 'uitest/har/session.har' },
  recordVideo: { dir: 'uitest/videos/' }
});
const page = await context.newPage();

// Enable tracing for failures
await context.tracing.start({ screenshots: true, snapshots: true, sources: true });

// Navigate and interact
await page.goto(TARGET_URL);
await page.fill('#email', 'test@uitest.local');
await page.click('button[type="submit"]');
await page.waitForURL('**/dashboard');

// Save trace on failure
await context.tracing.stop({ path: 'uitest/traces/test-name.zip' });
```

---

## Configuration Variables

Set these before launching the swarm. The qa-lead reads them from environment or from `uitest/config.json`:

```json
{
  "target_url": "http://localhost:3000",
  "base_url": "http://localhost:3000",
  "auth": {
    "signup_url": "/signup",
    "login_url": "/login",
    "logout_url": "/logout",
    "reset_url": "/forgot-password"
  },
  "test_users": {
    "admin": { "email": "admin@uitest.local", "password": "Admin!Test123" },
    "user": { "email": "user@uitest.local", "password": "User!Test456" },
    "readonly": { "email": "readonly@uitest.local", "password": "Read!Test789" }
  },
  "timeouts": {
    "navigation_ms": 10000,
    "element_ms": 5000,
    "network_idle_ms": 3000
  },
  "max_fix_iterations": 10,
  "min_pass_rate_to_continue": 0.5,
  "browsers": ["chromium", "firefox", "webkit"],
  "viewports": [
    { "name": "mobile", "width": 375, "height": 812 },
    { "name": "tablet", "width": 768, "height": 1024 },
    { "name": "desktop", "width": 1280, "height": 720 },
    { "name": "wide", "width": 1920, "height": 1080 }
  ],
  "cost_guardrail_per_hour": 15
}
```

---

## Launch Command

Feed this entire file as context, then issue:

```
Read UITEST.md. Target URL is {YOUR_APP_URL}.
Initialize the testing swarm, run Phase 1 through Phase 5.
Fix every defect you find. Loop until 100% or max iterations.
Generate the final report.
```

Or the one-liner:

```
UITEST target={YOUR_APP_URL} — full autonomous UAT, self-heal, loop to 100%.
```

---

## Cost & Model Routing

| Activity | Model | Rationale |
|----------|-------|-----------|
| Discovery crawl | Haiku | High-volume, simple page parsing |
| Form/nav/a11y testing | Sonnet | Moderate complexity, pattern matching |
| Auth/security testing | Opus | Critical reasoning for security edge cases |
| Bug fix implementation | Sonnet | Standard code changes |
| Blast radius analysis | Opus | Complex dependency reasoning |
| Report generation | Haiku | Template-based output |

Guardrail: **$15/hr max**. If cost exceeds this, qa-lead pauses non-critical agents and continues P0/P1 work only.

---

## Safety Rules

1. **NEVER** run against production without explicit human confirmation (Triple-Gate applies).
2. **NEVER** delete real user data. Only interact with test users created by the auth-tester.
3. **NEVER** modify database directly. All actions go through the UI or documented APIs.
4. **ALL** fix swarms must pass aqe-gate before merging.
5. **ALL** merges to main require Triple-Gate (3 human confirmations).
6. After **3 failed fix attempts** on the same bug, escalate to human via `bd human {bug-id}`.
7. **ALWAYS** commit and push before ending a session: `bd dolt push && git push`.
8. If the target application is unreachable for > 60 seconds, pause all agents and alert human.

---

## Session End Protocol

```bash
# 1. Close all open test bugs with status
bd list --json | jq '.[] | select(.status=="open")'
# For each: bd close or bd update with final status

# 2. Push all data
bd dolt push
git add -A
git commit -m "uitest: campaign results — {pass_rate}% pass rate"
git push

# 3. Update knowledge graph
gnx-analyze
neural-patterns

# 4. Final status
turbo-status
echo "UITEST COMPLETE: {pass_rate}% — report at uitest/reports/UITEST-FINAL-REPORT.md"
```

# UITEST Addendum v1.1.0
> Attach to UITEST.md v1.0.0 · Additions: RuVector memory, RVF audit, coherence gating, spec gap fixes

---

## A1. RuVector / AgentDB — Semantic Test Memory

The base spec uses `ruv-remember` for flat key-value storage. Replacing this with RuVector's
GNN-backed HNSW memory lets the swarm perform semantic queries against past failures — e.g.
"find failures structurally similar to this new one" — and accumulate learning across campaigns,
not just within a single run.

### Bootstrap addition (insert after step 3 in Environment Bootstrap)

```bash
# Install RuVector semantic memory stack
npx @ruvector/cli hooks init
npx @ruvector/cli hooks install   # wires into Claude Code session
npm install agentdb@alpha
npm install ruvector
```

### Agent memory usage

Replace all `ruv-remember` calls with AgentDB writes:

```javascript
const { AgentDB } = require('agentdb');
const db = new AgentDB({ dimensions: 384, persist: true, path: 'uitest/.agentdb' });

// Store a failure signature as a vector
await db.store({
  id: `failure-${bugId}`,
  embedding: await embed(bugDescription),   // use local ONNX model
  metadata: { form, field, testType, url, iteration }
});

// On each new failure, query for similar past failures before filing a new bug
const similar = await db.search(await embed(newFailureDescription), { k: 5 });
if (similar[0]?.score > 0.92) {
  // Likely a duplicate or variant — link rather than create new Bead
  bd update ${similar[0].metadata.bugId} --note "Recurrence: ${newFailureDescription}"
} else {
  bd create "BUG: ..." -t bug -p N
}
```

### Cross-campaign learning

AgentDB persists across sessions. On swarm init, query for known failure patterns on the
target URL before Phase 1 even begins:

```javascript
const knownPatterns = await db.search(await embed(TARGET_URL), {
  k: 20,
  filter: { url: TARGET_URL }
});
// Pass to qa-lead as pre-seeded risk areas — prioritize those pages in Phase 2
ruv-remember "preseeded-risks" JSON.stringify(knownPatterns.map(p => p.metadata))
```

---

## A2. RVF Cognitive Containers — Per-Agent Audit Trails

The base spec records test *results* but has no tamper-proof record of the testing *actions*
themselves. Packaging each agent's session as an RVF cognitive container gives you a
cryptographically witnessed, hash-chained audit trail of every browser action — useful for
compliance, client reporting, or debugging disputed results.

### Install

```bash
cargo install rvf-cli
npm install @ruvector/rvf
```

### Per-agent RVF session (add to each agent's teardown)

```bash
# At the end of each agent's work, seal its session into an RVF artifact
rvf-cli seal \
  --input uitest/reports/${AGENT_NAME}.json \
  --traces uitest/traces/${AGENT_NAME}/ \
  --screenshots uitest/screenshots/ \
  --output uitest/artifacts/${AGENT_NAME}.rvf \
  --sign ed25519 \
  --witness-chain enabled

# Verify integrity at any future point
rvf-cli verify uitest/artifacts/${AGENT_NAME}.rvf
```

Each `.rvf` file contains: the agent's full action log, all screenshots, all traces, a
hash-linked witness chain of every write, and an Ed25519 signature. The final report can
reference artifact hashes as evidence anchors.

### Add to Phase 5 report template

```markdown
## Artifact Integrity

| Agent | RVF File | Witness Chain | Signature |
|-------|----------|---------------|-----------|
| crawler | uitest/artifacts/crawler.rvf | ✅ verified | ed25519:abc123... |
| form-tester | uitest/artifacts/form-tester.rvf | ✅ verified | ed25519:def456... |
...
```

---

## A3. Prime Radiant Coherence Gate — Fix Validation

The base spec uses `aqe-gate` as the sole merge gate for fix swarms. Adding a Prime Radiant
coherence check catches fixes that pass the test mechanically but introduce semantic drift —
e.g. a validation bypass that makes the form test green but is logically incorrect.

### Install

```bash
cargo add prime-radiant --features simd
```

### Add to FIX SWARM INSTRUCTIONS (after step 5, before commit)

```bash
# Run coherence check on the affected module before committing
coherence_score=$(prime-radiant check \
  --files "$(gitnexus_impact --files src/components/TargetComponent.tsx --json | jq -r '.affected[]')" \
  --baseline main \
  --branch "fix-${BUG_ID}" \
  --output json | jq '.energy')

# Coherence ladder:
#   < 0.1  → safe to merge automatically
#   0.1–0.4 → flag for qa-lead review, proceed with note
#   0.4–0.7 → block merge, escalate to human
#   > 0.7  → revert, file as "fix-induced drift"

if (( $(echo "$coherence_score > 0.4" | bc -l) )); then
  echo "COHERENCE BLOCK: score=$coherence_score — escalating to human"
  bd human ${BUG_ID} --note "Fix candidate blocked by coherence gate (score: $coherence_score)"
  git checkout -- .
else
  git add -A && git commit -m "fix: ${BUG_ID} — coherence score ${coherence_score}"
fi
```

### Add coherence scores to final report

```markdown
## Fix Coherence Scores

| Bug ID | Fix Description | Coherence Score | Gate Result |
|--------|-----------------|-----------------|-------------|
| BUG-001 | Null check on submit handler | 0.03 | ✅ auto-merged |
| BUG-007 | Auth redirect bypass fix | 0.38 | ⚠️ merged with note |
| BUG-012 | Form validation skip | 0.71 | 🚫 reverted, escalated |
```

---

## A4. API Endpoint Fuzzing (api-verifier gap)

The base api-verifier does passive capture and targeted reverse calls, but does not fuzz
endpoint parameters. Add this pass after the reverse verification block:

```javascript
// Lightweight param fuzzing on each discovered endpoint
const FUZZ_PAYLOADS = {
  string: ['', ' ', '\x00', '<script>x</script>', "' OR 1=1--", '${7*7}', 'a'.repeat(10000)],
  number: [0, -1, 2147483647, -2147483648, 0.1, NaN, Infinity, ''],
  id:     ['0', '-1', '999999999', '../../../etc/passwd', 'null', 'undefined']
};

for (const endpoint of discoveredEndpoints) {
  for (const [param, type] of Object.entries(endpoint.params)) {
    for (const payload of FUZZ_PAYLOADS[type] ?? FUZZ_PAYLOADS.string) {
      const res = await apiCall(endpoint, { ...defaultParams, [param]: payload });
      if (res.status === 500) {
        bd create `API FUZZ: ${endpoint.method} ${endpoint.path} — 500 on param '${param}' with payload '${payload}'` -t bug -p 1
      }
      // Flag any 200 response to an obvious injection payload
      if (res.status === 200 && String(payload).includes("' OR 1=1")) {
        bd create `SECURITY: Possible SQLi on ${endpoint.path} param '${param}'` -t bug -p 0
      }
    }
  }
}
```

---

## A5. Memory Leak Detection Fix (load-tester gap)

`performance.memory` is Chromium-only and unreliable. Replace with Playwright's native
`page.metrics()` for cross-browser heap tracking:

```javascript
// Replace the memory monitoring block in load-tester with:
async function trackMemoryLeak(page, durationMs = 300000, intervalMs = 30000) {
  const samples = [];
  const start = Date.now();

  while (Date.now() - start < durationMs) {
    await page.waitForTimeout(intervalMs);
    const metrics = await page.metrics();
    samples.push({
      timestamp: Date.now() - start,
      jsHeapUsedMB: metrics.JSHeapUsedSize / 1024 / 1024,
      domNodes: metrics.Nodes,
      eventListeners: metrics.JSEventListeners
    });

    // Interact to keep session alive
    await page.mouse.move(100, 100);
  }

  // Simple linear regression to detect upward trend
  const heapValues = samples.map(s => s.jsHeapUsedMB);
  const trend = (heapValues.at(-1) - heapValues[0]) / heapValues[0];

  if (trend > 0.2) {   // >20% heap growth over session
    bd create `MEMORY LEAK: JS heap grew ${(trend*100).toFixed(1)}% over ${durationMs/60000}min session` -t bug -p 1
  }
  if (samples.at(-1).domNodes > samples[0].domNodes * 1.3) {
    bd create `DOM LEAK: Node count grew ${samples.at(-1).domNodes - samples[0].domNodes} over session` -t bug -p 2
  }

  return samples;
}
```

---

## A6. Cost Guardrail Implementation (config gap)

The `cost_guardrail_per_hour` config key exists but is never enforced. Add this to the
qa-lead loop, evaluated at the top of each iteration:

```javascript
// Add to qa-lead loop — check at start of each iteration
const COST_CONFIG = {
  haiku:  { input: 0.80,  output: 4.00  },   // per 1M tokens
  sonnet: { input: 3.00,  output: 15.00 },
  opus:   { input: 15.00, output: 75.00 }
};

function estimatedHourlyCost(tokenCounts, agentModelMap) {
  let total = 0;
  for (const [agent, counts] of Object.entries(tokenCounts)) {
    const model = agentModelMap[agent];
    const rates = COST_CONFIG[model];
    total += (counts.input / 1e6) * rates.input;
    total += (counts.output / 1e6) * rates.output;
  }
  return total * (3600 / elapsedSeconds());   // annualize to per-hour rate
}

const hourlyCost = estimatedHourlyCost(tokenCounts, AGENT_MODEL_MAP);
if (hourlyCost > config.cost_guardrail_per_hour) {
  console.warn(`COST GUARDRAIL: ~$${hourlyCost.toFixed(2)}/hr — suspending P2/P3 agents`);
  // Pause non-critical agents, continue only P0/P1 work
  for (const agent of ['a11y-tester', 'load-tester']) {
    rf-pause ${agent}
  }
  bd create `COST ALERT: Guardrail hit at $${hourlyCost.toFixed(2)}/hr — P2/P3 agents paused` -t task -p 1
}
```

---

## A7. Early Abort on Catastrophic Pass Rate (loop logic gap)

The base spec only stops early if `pass_rate < 0.95` after the full 10 iterations. There is
no early abort if the target is fundamentally broken. Add this check after the first two
iterations:

```
// Add to qa-lead LOOP after EVALUATE step, before GOTO:

if (iteration >= 2 && pass_rate < config.min_pass_rate_to_continue) {
  bd create "UITEST ABORTED: Pass rate ${pass_rate*100}% after iteration ${iteration} — below min threshold ${config.min_pass_rate_to_continue*100}%. Target may be non-functional." -t task -p 0 --flag human
  // Still generate a partial report so the team has evidence
  generate_partial_report(iteration, pass_rate, open_bugs)
  STOP
}
```

The existing `min_pass_rate_to_continue: 0.5` config value is now actually enforced. This
prevents burning 8 more iterations — and most of the cost budget — on an application that
is fundamentally broken and needs a human before automated testing can proceed.

---

## Updated config.json (incorporating all additions)

```json
{
  "target_url": "http://localhost:3000",
  "base_url": "http://localhost:3000",
  "auth": {
    "signup_url": "/signup",
    "login_url": "/login",
    "logout_url": "/logout",
    "reset_url": "/forgot-password"
  },
  "test_users": {
    "admin":    { "email": "admin@uitest.local",    "password": "Admin!Test123" },
    "user":     { "email": "user@uitest.local",     "password": "User!Test456" },
    "readonly": { "email": "readonly@uitest.local", "password": "Read!Test789" }
  },
  "timeouts": {
    "navigation_ms":   10000,
    "element_ms":       5000,
    "network_idle_ms":  3000
  },
  "max_fix_iterations": 10,
  "min_pass_rate_to_continue": 0.5,
  "early_abort_after_iteration": 2,
  "browsers": ["chromium", "firefox", "webkit"],
  "viewports": [
    { "name": "mobile",  "width": 375,  "height": 812  },
    { "name": "tablet",  "width": 768,  "height": 1024 },
    { "name": "desktop", "width": 1280, "height": 720  },
    { "name": "wide",    "width": 1920, "height": 1080 }
  ],
  "cost_guardrail_per_hour": 15,
  "memory": {
    "backend": "ruvector",
    "persist_path": "uitest/.agentdb",
    "similarity_dedup_threshold": 0.92
  },
  "coherence_gate": {
    "enabled": true,
    "auto_merge_below": 0.1,
    "review_below": 0.4,
    "block_above": 0.4
  },
  "audit": {
    "rvf_artifacts": true,
    "sign_method": "ed25519",
    "witness_chain": true
  },
  "fuzzing": {
    "api_params": true,
    "flag_500_responses": true,
    "flag_sqli_200_responses": true
  }
}
```

---

*Addendum authored against UITEST.md v1.0.0 · Stack additions: RuVector · AgentDB · RVF · Prime Radiant*
