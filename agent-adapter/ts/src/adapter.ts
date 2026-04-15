// =============================================================================
// TurboFlow Agent Adapter — Main Adapter Class
//
// High-level API that wraps the registry and active backend.
// This is the primary entry point for programmatic usage.
// =============================================================================

import type {
  BackendId,
  BackendInfo,
  ExecOptions,
  ExecResult,
  HealthCheckResult,
  McpServer,
} from './types.js';
import type { AgentBackend } from './backend.js';
import { registry, createBackend } from './registry.js';
import { BackendNotInstalledError, CapabilityNotSupportedError } from './errors.js';
import { Logger } from './logger.js';

export class AgentAdapter {
  private backend: AgentBackend;
  private readonly log = new Logger('adapter');

  constructor(backendId?: BackendId | string) {
    const id = backendId ?? process.env.TURBOFLOW_AGENT_BACKEND ?? 'claude';
    this.backend = createBackend(id);
    this.log.info(`Initialized with backend: ${this.backend.name}`);
  }

  /** Get the active backend */
  get activeBackend(): AgentBackend {
    return this.backend;
  }

  /** Get the active backend ID */
  get activeBackendId(): string {
    return this.backend.toInfo().id;
  }

  // ── Backend management ──────────────────────────────────────────────────

  /** Switch to a different backend */
  async switchBackend(id: BackendId | string): Promise<void> {
    const newBackend = createBackend(id);
    const installed = await newBackend.isInstalled();

    if (!installed) {
      throw new BackendNotInstalledError(id);
    }

    this.backend = newBackend;
    this.log.info(`Switched to backend: ${newBackend.name}`);
  }

  /** List all available backends */
  listBackends(): BackendInfo[] {
    return registry.listAll();
  }

  /** Get status of all backends (installed, version, etc.) */
  async status(): Promise<Array<BackendInfo & { installed: boolean; version: string | null }>> {
    const results = [];
    for (const id of registry.listIds()) {
      const backend = createBackend(id);
      const installed = await backend.isInstalled();
      const version = installed ? await backend.version() : null;
      results.push({
        ...backend.toInfo(),
        installed,
        version,
        active: id === this.activeBackendId,
      });
    }
    return results;
  }

  // ── Agent operations ────────────────────────────────────────────────────

  /** Execute a prompt through the active agent */
  async exec(prompt: string, options?: ExecOptions): Promise<ExecResult> {
    this.log.info(`Executing prompt via ${this.backend.name}`, {
      model: options?.model,
      headless: options?.headless,
      files: options?.files?.length,
    });

    const startTime = Date.now();
    const result = await this.backend.exec(prompt, options);

    this.log.info(`Execution complete`, {
      exitCode: result.exitCode,
      durationMs: result.durationMs,
      timedOut: result.timedOut,
    });

    return result;
  }

  /** Get agent version */
  async version(): Promise<string | null> {
    return this.backend.version();
  }

  /** Health check */
  async healthCheck(): Promise<HealthCheckResult> {
    return this.backend.healthCheck();
  }

  /** Install the active backend */
  async install(): Promise<void> {
    return this.backend.install();
  }

  // ── MCP operations ──────────────────────────────────────────────────────

  /** Register an MCP server */
  async mcpAdd(server: McpServer): Promise<void> {
    if (!this.backend.hasCapability('mcp')) {
      this.log.warn(`Backend '${this.backend.name}' does not support MCP — skipping`);
      return;
    }
    return this.backend.mcpAdd(server);
  }

  /** Remove an MCP server */
  async mcpRemove(name: string): Promise<void> {
    if (!this.backend.hasCapability('mcp')) return;
    return this.backend.mcpRemove(name);
  }

  /** List MCP servers */
  async mcpList(): Promise<McpServer[]> {
    if (!this.backend.hasCapability('mcp')) return [];
    return this.backend.mcpList();
  }

  // ── Capability checks ──────────────────────────────────────────────────

  /** Check if the active backend supports a capability */
  hasCapability(cap: string): boolean {
    return this.backend.hasCapability(cap as any);
  }

  /** Require a capability — throws if not supported */
  requireCapability(cap: string): void {
    if (!this.hasCapability(cap)) {
      throw new CapabilityNotSupportedError(this.activeBackendId, cap);
    }
  }

  // ── Model resolution ───────────────────────────────────────────────────

  /** Resolve a model tier name to a backend-specific model string */
  resolveModel(model: string): string {
    return this.backend.resolveModel(model);
  }
}
