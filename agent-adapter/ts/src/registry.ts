// =============================================================================
// TurboFlow Agent Adapter — Backend Registry (Factory + Registry Pattern)
//
// Central registry for all backends. Supports dynamic registration so
// third-party backends can be added without modifying core code.
// =============================================================================

import type { BackendId, BackendInfo } from './types.js';
import type { AgentBackend } from './backend.js';
import { UnknownBackendError } from './errors.js';
import { Logger } from './logger.js';

import { ClaudeBackend } from './backends/claude.js';
import { AiderBackend } from './backends/aider.js';
import { OpenHandsBackend } from './backends/openhands.js';

const log = new Logger('registry');

type BackendFactory = () => AgentBackend;

class BackendRegistry {
  private factories = new Map<string, BackendFactory>();
  private instances = new Map<string, AgentBackend>();

  constructor() {
    // Register built-in backends
    this.register('claude', () => new ClaudeBackend());
    this.register('aider', () => new AiderBackend());
    this.register('openhands', () => new OpenHandsBackend());
  }

  /** Register a new backend factory */
  register(id: string, factory: BackendFactory): void {
    this.factories.set(id, factory);
    log.debug(`Backend registered: ${id}`);
  }

  /** Get or create a backend instance */
  get(id: string): AgentBackend {
    // Return cached instance
    const cached = this.instances.get(id);
    if (cached) return cached;

    // Create new instance
    const factory = this.factories.get(id);
    if (!factory) {
      throw new UnknownBackendError(id, this.listIds());
    }

    const instance = factory();
    this.instances.set(id, instance);
    return instance;
  }

  /** Check if a backend is registered */
  has(id: string): boolean {
    return this.factories.has(id);
  }

  /** List all registered backend IDs */
  listIds(): string[] {
    return [...this.factories.keys()];
  }

  /** List all registered backends with metadata */
  listAll(): BackendInfo[] {
    return this.listIds().map((id) => this.get(id).toInfo());
  }

  /** Clear cached instances (useful for testing) */
  clearInstances(): void {
    this.instances.clear();
  }
}

/** Singleton registry */
export const registry = new BackendRegistry();

/**
 * Factory function — get a backend by ID.
 * Shorthand for registry.get().
 */
export function createBackend(id: BackendId | string): AgentBackend {
  return registry.get(id);
}
