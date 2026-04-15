// =============================================================================
// TurboFlow Agent Adapter — Public API
// =============================================================================

// Core
export { AgentAdapter } from './adapter.js';
export { AgentBackend } from './backend.js';
export { registry, createBackend } from './registry.js';

// Backends
export { ClaudeBackend } from './backends/claude.js';
export { AiderBackend } from './backends/aider.js';
export { OpenHandsBackend } from './backends/openhands.js';

// Types
export type {
  BackendId,
  BackendCapabilities,
  BackendInfo,
  ExecOptions,
  ExecResult,
  HealthCheckResult,
  McpServer,
  ModelTier,
  LogLevel,
} from './types.js';

// Errors
export {
  AdapterError,
  BackendNotInstalledError,
  UnknownBackendError,
  CapabilityNotSupportedError,
  ExecError,
  TimeoutError,
  ConfigError,
} from './errors.js';

// Utilities
export { Logger } from './logger.js';
export { run, commandExists } from './process.js';
