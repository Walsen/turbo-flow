// =============================================================================
// TurboFlow Agent Adapter — OpenHands Backend
//
// Wraps OpenHands (https://github.com/All-Hands-AI/OpenHands).
// MIT licensed, multi-model, MCP-compatible.
// Runs via CLI or Docker container.
// =============================================================================

import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { homedir } from 'node:os';
import { AgentBackend } from '../backend.js';
import { run, commandExists } from '../process.js';
import type {
  BackendCapabilities,
  ExecOptions,
  ExecResult,
  HealthCheckResult,
  McpServer,
} from '../types.js';

const DEFAULT_IMAGE = 'ghcr.io/all-hands-ai/openhands:latest';

export class OpenHandsBackend extends AgentBackend {
  readonly name = 'OpenHands';
  readonly description = 'Open-source AI software engineer (MIT license)';
  readonly url = 'https://github.com/All-Hands-AI/OpenHands';
  readonly license = 'MIT';

  readonly capabilities: BackendCapabilities = {
    mcp: true,
    agentTeams: false,
    multiModel: true,
    interactive: false,
    headless: true,
    streaming: true,
    bedrock: false,
    worktrees: true,
  };

  private readonly image: string;

  constructor() {
    super('openhands');
    this.image = process.env.OPENHANDS_IMAGE ?? DEFAULT_IMAGE;
  }

  resolveModel(model: string): string {
    const tierMap: Record<string, string> = {
      opus: 'anthropic/claude-opus-4-20250514',
      sonnet: 'anthropic/claude-sonnet-4-20250514',
      haiku: 'anthropic/claude-haiku-4-5-20251001',
    };
    return tierMap[model] ?? model;
  }

  private detectApiKey(model: string): string | undefined {
    if (process.env.LLM_API_KEY) return process.env.LLM_API_KEY;
    if (model.startsWith('anthropic/')) return process.env.ANTHROPIC_API_KEY;
    if (model.startsWith('openai/')) return process.env.OPENAI_API_KEY;
    return process.env.ANTHROPIC_API_KEY ?? process.env.OPENAI_API_KEY;
  }

  async exec(prompt: string, options: ExecOptions = {}): Promise<ExecResult> {
    const model = options.model
      ? this.resolveModel(options.model)
      : process.env.LLM_MODEL ?? 'anthropic/claude-sonnet-4-20250514';

    const apiKey = this.detectApiKey(model);
    if (!apiKey) {
      return {
        exitCode: 1,
        stdout: '',
        stderr: 'No API key found. Set LLM_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY.',
        durationMs: 0,
        timedOut: false,
      };
    }

    // Add file context to prompt
    let fullPrompt = prompt;
    if (options.files?.length) {
      fullPrompt = `Focus on these files: ${options.files.join(', ')}. ${prompt}`;
    }

    const env = {
      LLM_MODEL: model,
      LLM_API_KEY: apiKey,
      ...options.env,
    };

    // Prefer CLI
    if (await commandExists('openhands')) {
      return run({
        command: 'openhands',
        args: ['run', '--task', fullPrompt, ...(options.extraArgs ?? [])],
        cwd: options.cwd,
        env,
        timeout: options.timeout,
        stream: true,
      });
    }

    // Fallback to Docker
    if (await commandExists('docker')) {
      const cwd = options.cwd ?? process.cwd();
      return run({
        command: 'docker',
        args: [
          'run', '--rm',
          '-e', `LLM_MODEL=${model}`,
          '-e', `LLM_API_KEY=${apiKey}`,
          '-v', `${cwd}:/workspace:rw`,
          this.image,
          'python', '-m', 'openhands.core.main',
          '-t', fullPrompt,
          ...(options.extraArgs ?? []),
        ],
        timeout: options.timeout,
        stream: true,
      });
    }

    return {
      exitCode: 1,
      stdout: '',
      stderr: 'Neither openhands CLI nor Docker found. Run: pip install openhands',
      durationMs: 0,
      timedOut: false,
    };
  }

  async version(): Promise<string | null> {
    if (await commandExists('openhands')) {
      const result = await run({ command: 'openhands', args: ['--version'], timeout: 10_000 });
      return result.exitCode === 0 ? result.stdout.trim() : null;
    }

    if (await commandExists('docker')) {
      const result = await run({
        command: 'docker',
        args: ['image', 'inspect', this.image, '--format', '{{index .RepoTags 0}}'],
        timeout: 10_000,
      });
      return result.exitCode === 0 ? `docker: ${result.stdout.trim()}` : null;
    }

    return null;
  }

  async isInstalled(): Promise<boolean> {
    if (await commandExists('openhands')) return true;

    // Check if Docker image is pulled
    if (await commandExists('docker')) {
      const result = await run({
        command: 'docker',
        args: ['image', 'inspect', this.image],
        timeout: 10_000,
      });
      return result.exitCode === 0;
    }

    return false;
  }

  async healthCheck(): Promise<HealthCheckResult> {
    const installed = await this.isInstalled();
    const version = installed ? await this.version() : null;
    const warnings: string[] = [];
    const details: Record<string, string | boolean> = {};

    details.cliAvailable = await commandExists('openhands');
    details.dockerAvailable = await commandExists('docker');

    if (details.dockerAvailable) {
      const imgResult = await run({
        command: 'docker',
        args: ['image', 'inspect', this.image],
        timeout: 10_000,
      });
      details.imagePulled = imgResult.exitCode === 0;
      if (!details.imagePulled) {
        warnings.push(`Docker image not pulled. Run: docker pull ${this.image}`);
      }
    }

    // Check providers
    const providers: string[] = [];
    if (process.env.ANTHROPIC_API_KEY) providers.push('Anthropic');
    if (process.env.OPENAI_API_KEY) providers.push('OpenAI');
    if (process.env.LLM_MODEL) details.model = process.env.LLM_MODEL;

    if (providers.length === 0 && !process.env.LLM_API_KEY) {
      warnings.push('No API key set. Set LLM_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY');
    }

    details.providers = providers.join(', ') || 'none';

    return {
      installed,
      version,
      provider: providers[0] ?? null,
      details,
      warnings,
    };
  }

  async install(): Promise<void> {
    this.log.info('Installing OpenHands...');

    // Try pip
    if (await commandExists('pip') || await commandExists('pip3')) {
      const pipCmd = await commandExists('pip3') ? 'pip3' : 'pip';
      const result = await run({
        command: pipCmd,
        args: ['install', '--user', 'openhands'],
        timeout: 180_000,
        stream: true,
      });
      if (result.exitCode === 0) {
        this.log.info('OpenHands installed (pip)');
        return;
      }
    }

    // Try Docker pull
    if (await commandExists('docker')) {
      const result = await run({
        command: 'docker',
        args: ['pull', this.image],
        timeout: 300_000,
        stream: true,
      });
      if (result.exitCode === 0) {
        this.log.info('OpenHands Docker image pulled');
        return;
      }
    }

    throw new Error(`OpenHands installation failed. Try: pip install openhands or docker pull ${this.image}`);
  }

  // ── MCP support via config file ─────────────────────────────────────────

  private get mcpConfigPath(): string {
    return join(homedir(), '.openhands', 'mcp_servers.json');
  }

  private readMcpConfig(): Record<string, { command: string; args?: string[] }> {
    try {
      if (existsSync(this.mcpConfigPath)) {
        return JSON.parse(readFileSync(this.mcpConfigPath, 'utf-8'));
      }
    } catch {
      this.log.warn('Failed to read MCP config');
    }
    return {};
  }

  private writeMcpConfig(config: Record<string, { command: string; args?: string[] }>): void {
    const dir = join(homedir(), '.openhands');
    mkdirSync(dir, { recursive: true });
    writeFileSync(this.mcpConfigPath, JSON.stringify(config, null, 2));
  }

  async mcpAdd(server: McpServer): Promise<void> {
    const config = this.readMcpConfig();
    config[server.name] = { command: server.command, args: server.args };
    this.writeMcpConfig(config);
    this.log.info(`MCP server '${server.name}' registered (openhands config)`);
  }

  async mcpRemove(name: string): Promise<void> {
    const config = this.readMcpConfig();
    delete config[name];
    this.writeMcpConfig(config);
  }

  async mcpList(): Promise<McpServer[]> {
    const config = this.readMcpConfig();
    return Object.entries(config).map(([name, val]) => ({
      name,
      command: val.command,
      args: val.args,
    }));
  }
}
