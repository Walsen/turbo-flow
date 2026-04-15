// =============================================================================
// TurboFlow Agent Adapter — Claude Code Backend
//
// Default backend. Wraps the `claude` CLI.
// Full feature support: MCP, Agent Teams, Bedrock, interactive + headless.
// =============================================================================

import { AgentBackend } from '../backend.js';
import { run, commandExists } from '../process.js';
import type {
  BackendCapabilities,
  ExecOptions,
  ExecResult,
  HealthCheckResult,
  McpServer,
} from '../types.js';

export class ClaudeBackend extends AgentBackend {
  readonly name = 'Claude Code';
  readonly description = 'Anthropic\'s agentic coding CLI with MCP, Agent Teams, and Bedrock support';
  readonly url = 'https://claude.ai/code';
  readonly license = 'Proprietary';

  readonly capabilities: BackendCapabilities = {
    mcp: true,
    agentTeams: true,
    multiModel: false,
    interactive: true,
    headless: true,
    streaming: true,
    bedrock: true,
    worktrees: true,
  };

  constructor() {
    super('claude');
  }

  resolveModel(model: string): string {
    const isBedrock = process.env.CLAUDE_CODE_USE_BEDROCK === '1';

    const tierMap: Record<string, { bedrock: string; direct: string }> = {
      opus: {
        bedrock: process.env.ANTHROPIC_DEFAULT_OPUS_MODEL ?? 'us.anthropic.claude-opus-4-6-v1',
        direct: 'claude-opus-4-20250514',
      },
      sonnet: {
        bedrock: process.env.ANTHROPIC_DEFAULT_SONNET_MODEL ?? 'us.anthropic.claude-sonnet-4-6',
        direct: 'claude-sonnet-4-20250514',
      },
      haiku: {
        bedrock: process.env.ANTHROPIC_DEFAULT_HAIKU_MODEL ?? 'us.anthropic.claude-haiku-4-5-20251001-v1:0',
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

    if (options.printOnly) {
      args.push('--print');
    }

    if (options.headless) {
      // Headless: pipe prompt via --print flag (non-interactive)
      args.push('--print', prompt);
      return run({
        command: 'claude',
        args: [...args, ...(options.extraArgs ?? [])],
        cwd: options.cwd,
        env: options.env,
        timeout: options.timeout,
        stream: true,
      });
    }

    // Interactive: pass prompt as positional arg
    args.push(...(options.extraArgs ?? []), prompt);

    return run({
      command: 'claude',
      args,
      cwd: options.cwd,
      env: options.env,
      timeout: options.timeout,
      stream: true,
    });
  }

  async version(): Promise<string | null> {
    const result = await run({ command: 'claude', args: ['--version'], timeout: 10_000 });
    return result.exitCode === 0 ? result.stdout.trim() : null;
  }

  async isInstalled(): Promise<boolean> {
    return commandExists('claude');
  }

  async healthCheck(): Promise<HealthCheckResult> {
    const installed = await this.isInstalled();
    const version = installed ? await this.version() : null;
    const warnings: string[] = [];
    const details: Record<string, string | boolean> = {};

    // Provider detection
    const isBedrock = process.env.CLAUDE_CODE_USE_BEDROCK === '1';
    const hasApiKey = !!process.env.ANTHROPIC_API_KEY;

    if (isBedrock) {
      details.provider = 'Amazon Bedrock';
      details.region = process.env.AWS_REGION ?? 'us-east-1';
      details.awsProfile = process.env.AWS_PROFILE ?? '(none)';
      if (!process.env.AWS_PROFILE && !process.env.AWS_ACCESS_KEY_ID) {
        warnings.push('Bedrock enabled but no AWS credentials detected');
      }
    } else if (hasApiKey) {
      details.provider = 'Anthropic API (direct)';
    } else {
      details.provider = 'not configured';
      warnings.push('No auth configured. Set ANTHROPIC_API_KEY or CLAUDE_CODE_USE_BEDROCK=1');
    }

    details.agentTeams = process.env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS === '1';

    // MCP server count
    if (installed) {
      const mcpResult = await run({ command: 'claude', args: ['mcp', 'list'], timeout: 10_000 });
      if (mcpResult.exitCode === 0) {
        const lines = mcpResult.stdout.trim().split('\n').filter(Boolean);
        details.mcpServers = `${lines.length} registered`;
      }
    }

    return { installed, version, provider: details.provider as string, details, warnings };
  }

  async install(): Promise<void> {
    this.log.info('Installing Claude Code...');

    // Try native installer
    const native = await run({
      command: 'bash',
      args: ['-c', 'curl -fsSL https://claude.ai/install.sh | bash'],
      timeout: 120_000,
      stream: true,
    });

    if (native.exitCode === 0 && await this.isInstalled()) {
      this.log.info('Claude Code installed (native)');
      return;
    }

    // Fallback to npm
    const npm = await run({
      command: 'npm',
      args: ['install', '-g', '@anthropic-ai/claude-code'],
      timeout: 120_000,
      stream: true,
    });

    if (npm.exitCode === 0 && await this.isInstalled()) {
      this.log.info('Claude Code installed (npm)');
      return;
    }

    throw new Error('Claude Code installation failed. Try: curl -fsSL https://claude.ai/install.sh | bash');
  }

  async mcpAdd(server: McpServer): Promise<void> {
    const args = ['mcp', 'add', server.name, '--'];
    args.push(server.command);
    if (server.args) args.push(...server.args);

    const result = await run({ command: 'claude', args, timeout: 15_000 });
    if (result.exitCode === 0) {
      this.log.info(`MCP server '${server.name}' registered`);
    } else {
      this.log.warn(`MCP registration failed for '${server.name}': ${result.stderr}`);
    }
  }

  async mcpRemove(name: string): Promise<void> {
    await run({ command: 'claude', args: ['mcp', 'remove', name], timeout: 10_000 });
  }

  async mcpList(): Promise<McpServer[]> {
    const result = await run({ command: 'claude', args: ['mcp', 'list'], timeout: 10_000 });
    if (result.exitCode !== 0) return [];

    // Parse claude mcp list output (format varies, return raw names)
    return result.stdout
      .trim()
      .split('\n')
      .filter(Boolean)
      .map((line) => ({ name: line.trim(), command: '' }));
  }
}
