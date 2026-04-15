# TurboFlow Agent Adapter Interface

Provider-independent abstraction layer between TurboFlow's orchestration (Ruflo) and agent CLI backends. Built with TypeScript using Strategy + Factory + Registry patterns.

## Quick Start

```bash
# Build
cd agent-adapter && npm install && npm run build

# CLI
node dist/cli.js status
node dist/cli.js exec "implement the login feature"
node dist/cli.js exec --model sonnet --file src/auth.ts "add error handling"

# Shell integration (adds agent-* functions)
source agent-adapter/shell-integration.sh
agent-status
agent-exec "refactor the payment module"
agent-switch aider
```

## Environment

```bash
TURBOFLOW_AGENT_BACKEND=claude|aider|openhands  # default: claude
TF_ADAPTER_LOG_LEVEL=debug|info|warn|error      # default: info
```

## CLI Commands

```
tf-adapter exec <prompt>          Execute a prompt through the active agent
tf-adapter status                 Show all backends and their status
tf-adapter health                 Health check on the active backend
tf-adapter switch <backend>       Switch backend
tf-adapter install <backend>      Install a backend
tf-adapter backends               List registered backends
tf-adapter mcp add <name> <cmd>   Register MCP server
tf-adapter mcp list               List MCP servers
tf-adapter resolve-model <tier>   Resolve model tier to backend-specific string
```

## Programmatic Usage

```typescript
import { AgentAdapter, registry } from '@turboflow/agent-adapter';

const adapter = new AgentAdapter('claude');

// Execute
const result = await adapter.exec('implement login', {
  model: 'sonnet',
  files: ['src/auth.ts'],
  headless: true,
});

// Switch backend
await adapter.switchBackend('aider');

// Register custom backend
import { AgentBackend } from '@turboflow/agent-adapter';

class MyBackend extends AgentBackend { /* ... */ }
registry.register('my-backend', () => new MyBackend());
```

## Architecture

```
src/
├── types.ts              Type definitions
├── errors.ts             Typed error hierarchy
├── logger.ts             Structured logger
├── process.ts            Child process runner with timeout + streaming
├── backend.ts            Abstract backend class (Strategy pattern)
├── registry.ts           Backend registry (Factory + Registry pattern)
├── adapter.ts            Main adapter class (high-level API)
├── cli.ts                CLI entry point (Commander)
└── backends/
    ├── claude.ts          Claude Code backend
    ├── aider.ts           Aider backend
    └── openhands.ts       OpenHands backend
```

## Backend Comparison

| Feature | Claude Code | Aider | OpenHands |
|---|---|---|---|
| MCP tools | ✓ | ✗ | ✓ |
| Agent Teams | ✓ | ✗ | ✗ |
| Multi-model | ✗ | ✓ | ✓ |
| Interactive | ✓ | ✓ | ✗ |
| Bedrock | ✓ | ✓ | ✗ |
| License | Proprietary | Apache-2.0 | MIT |

## Adding a New Backend

1. Create `src/backends/<name>.ts` extending `AgentBackend`
2. Implement all abstract methods
3. Register in `src/registry.ts` or dynamically via `registry.register()`
