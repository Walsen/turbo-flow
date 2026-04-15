// =============================================================================
// TurboFlow Agent Adapter — Aider Backend
//
// Wraps the `aider` CLI (https://aider.chat).
// Multi-model support (OpenAI, Anthropic, Bedrock, local models).
// Does NOT support: MCP, Agent Teams.
// =============================================================================

import { AgentBackend } from '../backend.js';
import { run, commandExists } from '../process.js';
import type {
  BackendCapabilities,
  ExecOptions,
  ExecResult,
  HealthCheckResult,
} from '../types.js';

export class AiderBackend extends AgentBackend {
  readonly name = 'Aider';
  readonly description = 'AI pair programming CLI with multi-model support (Apache 2.0)';
  readonly url = 'https://aider.chat';
  readonly license = 'Apache-2.0';

  readonly capabilities: BackendCapabilities = {
    mcp: false,
    agentTeams: false,
    multiModel: true,
    interactive: true,
    headless: true,
    streaming: true,
    bedrock: true,
    worktrees: true,
  };

  constructor() {
    super('aider');
  }

  resolveModel(model: string): string {
    const isBedrock = process.env.CLAUDE_CODE_USE_BEDROCK === '1';

    const tierMap: Record<string, { bedrock: string; direct: string }> = {
      opus: {
        bedrock: `bedrock/${process.env.ANTHROPIC_DEFAULT_OPUS_MODEL ?? 'us.anthropic.claude-opus-4-6-v1'}`,
        direct: 'claude-3-opus-20240229',
      },
      sonnet: {
        bedrock: `bedrock/${process.env.ANTHROPIC_DEFAULT_SONNET_MODEL ?? 'us.anthropic.claude-sonnet-4-6'}`,
        direct: 'claude-sonnet-4-20250514',
      },
      haiku: {
        bedrock: `bedrock/${process.env.ANTHROPIC_DEFAULT_HAIKU_MODEL ?? 'us.anthropic.claude-haiku-4-5-20251001-v1:0'}`,
        direct: 'claude-haiku-4-5-20251001',
      },
    };

    const tier = tierMap[model];
    if (tier) {
      return isBedrock ? tier.bedrock : tier.direct;
    }
    return model;
  }

  async exec(prompt: string, options: ExecOptions = {}): Promise<ExecResult> {
    const args: string[] = [];

    if (options.model) {
      args.push('--model', this.resolveModel(options.model));
    }

    // Add target files
    if (options.files?.length) {
      args.push(...options.files);
    }

    if (options.headless || options.printOnly) {
      // Non-interactive: --message mode
      args.push('--message', prompt, '--no-auto-commits', '--yes');
    }

    args.push(...(options.extraArgs ?? []));

    return run({
      command: 'aider',
      args,
      cwd: options.cwd,
      env: options.env,
      timeout: options.timeout,
      stream: true,
    });
  }

  async version(): Promise<string | null> {
    const result = await run({ command: 'aider', args: ['--version'], timeout: 10_000 });
    return result.exitCode === 0 ? result.stdout.trim() : null;
  }

  async isInstalled(): Promise<boolean> {
    return commandExists('aider');
  }

  async healthCheck(): Promise<HealthCheckResult> {
    const installed = await this.isInstalled();
    const version = installed ? await this.version() : null;
    const warnings: string[] = [];
    const details: Record<string, string | boolean> = {};

    // Check model providers
    const providers: string[] = [];
    if (process.env.ANTHROPIC_API_KEY) providers.push('Anthropic');
    if (process.env.CLAUDE_CODE_USE_BEDROCK === '1') providers.push('Bedrock');
    if (process.env.OPENAI_API_KEY) providers.push('OpenAI');
    if (process.env.OPENROUTER_API_KEY) providers.push('OpenRouter');

    if (providers.length === 0) {
      warnings.push('No model provider configured. Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or OPENROUTER_API_KEY');
    }

    details.providers = providers.join(', ') || 'none';
    details.mcp = false;
    details.agentTeams = false;

    return {
      installed,
      version,
      provider: providers[0] ?? null,
      details,
      warnings,
    };
  }

  async install(): Promise<void> {
    this.log.info('Installing Aider...');

    // Try pipx first (isolated install)
    if (await commandExists('pipx')) {
      const result = await run({
        command: 'pipx',
        args: ['install', 'aider-chat'],
        timeout: 120_000,
        stream: true,
      });
      if (result.exitCode === 0) {
        this.log.info('Aider installed (pipx)');
        return;
      }
    }

    // Fallback to pip
    const pipCmd = await commandExists('pip3') ? 'pip3' : 'pip';
    const result = await run({
      command: pipCmd,
      args: ['install', '--user', 'aider-chat'],
      timeout: 120_000,
      stream: true,
    });

    if (result.exitCode === 0) {
      this.log.info('Aider installed (pip)');
      return;
    }

    throw new Error('Aider installation failed. Try: pipx install aider-chat');
  }
}
