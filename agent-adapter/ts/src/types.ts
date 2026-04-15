// =============================================================================
// TurboFlow Agent Adapter — Core Types
// =============================================================================

/** Supported agent backend identifiers */
export type BackendId = 'claude' | 'aider' | 'openhands';

/** Capability flags — what a backend can do */
export interface BackendCapabilities {
  /** MCP tool registration */
  mcp: boolean;
  /** Multi-agent spawning (Claude Agent Teams) */
  agentTeams: boolean;
  /** Can use multiple LLM providers */
  multiModel: boolean;
  /** Supports interactive CLI sessions */
  interactive: boolean;
  /** Supports non-interactive / prompt-only mode */
  headless: boolean;
  /** Streams output in real-time */
  streaming: boolean;
  /** Native AWS Bedrock support */
  bedrock: boolean;
  /** Can operate in git worktrees */
  worktrees: boolean;
}

/** Options for agent-exec */
export interface ExecOptions {
  /** Target file(s) for the agent to work on */
  files?: string[];
  /** Override model (backend-specific or tier name: opus/sonnet/haiku) */
  model?: string;
  /** Non-interactive mode */
  headless?: boolean;
  /** Print-only mode — output to stdout, no file writes */
  printOnly?: boolean;
  /** Working directory */
  cwd?: string;
  /** Environment variable overrides */
  env?: Record<string, string>;
  /** Timeout in milliseconds (0 = no timeout) */
  timeout?: number;
  /** Extra backend-specific arguments */
  extraArgs?: string[];
}

/** Result from agent-exec */
export interface ExecResult {
  /** Exit code (0 = success) */
  exitCode: number;
  /** Stdout output */
  stdout: string;
  /** Stderr output */
  stderr: string;
  /** Execution time in milliseconds */
  durationMs: number;
  /** Whether the process was killed by timeout */
  timedOut: boolean;
}

/** MCP server registration info */
export interface McpServer {
  name: string;
  command: string;
  args?: string[];
  env?: Record<string, string>;
}

/** Health check result */
export interface HealthCheckResult {
  installed: boolean;
  version: string | null;
  provider: string | null;
  details: Record<string, string | boolean>;
  warnings: string[];
}

/** Model tier names that get resolved per-backend */
export type ModelTier = 'opus' | 'sonnet' | 'haiku';

/** Log levels */
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

/** Backend metadata returned by registry */
export interface BackendInfo {
  id: BackendId;
  name: string;
  description: string;
  url: string;
  license: string;
  capabilities: BackendCapabilities;
}
