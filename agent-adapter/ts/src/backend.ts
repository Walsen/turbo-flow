// =============================================================================
// TurboFlow Agent Adapter — Abstract Backend (Strategy Pattern)
//
// Each backend implements this interface. The adapter dispatches to the
// active backend without knowing the implementation details.
// =============================================================================

import type {
  BackendCapabilities,
  BackendId,
  ExecOptions,
  ExecResult,
  HealthCheckResult,
  McpServer,
} from './types.js';
import { Logger } from './logger.js';

export abstract class AgentBackend {
  protected readonly log: Logger;

  constructor(protected readonly id: BackendId) {
    this.log = new Logger(`backend:${id}`);
  }

  /** Human-readable name */
  abstract readonly name: string;

  /** Short description */
  abstract readonly description: string;

  /** Project URL */
  abstract readonly url: string;

  /** License identifier */
  abstract readonly license: string;

  /** What this backend supports */
  abstract readonly capabilities: BackendCapabilities;

  // ── Core operations ─────────────────────────────────────────────────────

  /** Execute a prompt through the agent */
  abstract exec(prompt: string, options?: ExecOptions): Promise<ExecResult>;

  /** Get the agent version string */
  abstract version(): Promise<string | null>;

  /** Check if the agent is installed and reachable */
  abstract isInstalled(): Promise<boolean>;

  /** Full health check */
  abstract healthCheck(): Promise<HealthCheckResult>;

  /** Install the agent backend */
  abstract install(): Promise<void>;

  // ── MCP operations (optional) ───────────────────────────────────────────

  /** Register an MCP server. No-op if MCP not supported. */
  async mcpAdd(server: McpServer): Promise<void> {
    this.log.warn(`MCP not supported by ${this.name}`);
  }

  /** Remove an MCP server. No-op if MCP not supported. */
  async mcpRemove(name: string): Promise<void> {
    this.log.warn(`MCP not supported by ${this.name}`);
  }

  /** List registered MCP servers. Empty if not supported. */
  async mcpList(): Promise<McpServer[]> {
    return [];
  }

  // ── Model resolution ────────────────────────────────────────────────────

  /**
   * Resolve a TurboFlow model tier name (opus/sonnet/haiku) to a
   * backend-specific model string. Pass-through for unknown names.
   */
  abstract resolveModel(model: string): string;

  // ── Helpers ─────────────────────────────────────────────────────────────

  /** Check if a specific capability is supported */
  hasCapability(cap: keyof BackendCapabilities): boolean {
    return this.capabilities[cap];
  }

  /** Get backend info as a plain object */
  toInfo() {
    return {
      id: this.id,
      name: this.name,
      description: this.description,
      url: this.url,
      license: this.license,
      capabilities: { ...this.capabilities },
    };
  }
}
