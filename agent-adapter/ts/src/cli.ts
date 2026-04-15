#!/usr/bin/env node
// =============================================================================
// TurboFlow Agent Adapter — CLI
//
// Usage:
//   tf-adapter exec "implement login feature"
//   tf-adapter exec --model sonnet --file src/auth.ts "add error handling"
//   tf-adapter status
//   tf-adapter health
//   tf-adapter switch aider
//   tf-adapter install aider
//   tf-adapter mcp add ruflo "npx -y ruflo@latest"
//   tf-adapter mcp list
//   tf-adapter backends
//   tf-adapter version
// =============================================================================

import { Command } from 'commander';
import { AgentAdapter } from './adapter.js';
import { registry } from './registry.js';
import { AdapterError } from './errors.js';

const program = new Command();

program
  .name('tf-adapter')
  .description('TurboFlow Agent Adapter — provider-independent agent CLI abstraction')
  .version('0.1.0');

// ── exec ────────────────────────────────────────────────────────────────────
program
  .command('exec')
  .description('Execute a prompt through the active agent backend')
  .argument('<prompt>', 'The prompt to send to the agent')
  .option('-f, --file <paths...>', 'Target file(s) for the agent')
  .option('-m, --model <model>', 'Model override (opus/sonnet/haiku or backend-specific)')
  .option('--headless', 'Non-interactive mode')
  .option('--print', 'Print-only mode (no file writes)')
  .option('-b, --backend <backend>', 'Override backend for this command')
  .option('-t, --timeout <ms>', 'Timeout in milliseconds', parseInt)
  .action(async (prompt: string, opts) => {
    const adapter = new AgentAdapter(opts.backend);
    const result = await adapter.exec(prompt, {
      files: opts.file,
      model: opts.model,
      headless: opts.headless,
      printOnly: opts.print,
      timeout: opts.timeout,
    });
    process.exit(result.exitCode);
  });

// ── status ──────────────────────────────────────────────────────────────────
program
  .command('status')
  .description('Show status of all agent backends')
  .action(async () => {
    const adapter = new AgentAdapter();
    const statuses = await adapter.status();

    console.log('╔══════════════════════════════════════════╗');
    console.log('║   TurboFlow Agent Adapter Status          ║');
    console.log('╚══════════════════════════════════════════╝');
    console.log('');

    for (const s of statuses) {
      const active = (s as any).active ? ' (active)' : '';
      const installed = s.installed ? '✓' : '✗';
      const ver = s.version ? ` — ${s.version}` : '';
      console.log(`  ${installed} ${s.name}${active}${ver}`);
      console.log(`    ${s.description}`);

      const caps = Object.entries(s.capabilities)
        .filter(([, v]) => v)
        .map(([k]) => k);
      console.log(`    Capabilities: ${caps.join(', ')}`);
      console.log('');
    }
  });

// ── health ──────────────────────────────────────────────────────────────────
program
  .command('health')
  .description('Run health check on the active backend')
  .option('-b, --backend <backend>', 'Check a specific backend')
  .action(async (opts) => {
    const adapter = new AgentAdapter(opts.backend);
    const health = await adapter.healthCheck();

    console.log(`Backend: ${adapter.activeBackendId}`);
    console.log(`Installed: ${health.installed ? '✓' : '✗'}`);
    console.log(`Version: ${health.version ?? 'unknown'}`);
    console.log(`Provider: ${health.provider ?? 'not configured'}`);

    if (Object.keys(health.details).length > 0) {
      console.log('Details:');
      for (const [k, v] of Object.entries(health.details)) {
        console.log(`  ${k}: ${v}`);
      }
    }

    if (health.warnings.length > 0) {
      console.log('Warnings:');
      for (const w of health.warnings) {
        console.log(`  ⚠ ${w}`);
      }
    }
  });

// ── switch ──────────────────────────────────────────────────────────────────
program
  .command('switch')
  .description('Switch the active agent backend')
  .argument('<backend>', 'Backend to switch to (claude, aider, openhands)')
  .action(async (backend: string) => {
    const adapter = new AgentAdapter();
    try {
      await adapter.switchBackend(backend);
      console.log(`✓ Switched to ${backend}`);
      const ver = await adapter.version();
      if (ver) console.log(`  Version: ${ver}`);
    } catch (err) {
      if (err instanceof AdapterError) {
        console.error(`✗ ${err.message}`);
        process.exit(1);
      }
      throw err;
    }
  });

// ── install ─────────────────────────────────────────────────────────────────
program
  .command('install')
  .description('Install an agent backend')
  .argument('<backend>', 'Backend to install (claude, aider, openhands)')
  .action(async (backend: string) => {
    const b = registry.get(backend);
    try {
      await b.install();
      console.log(`✓ ${b.name} installed`);
    } catch (err) {
      console.error(`✗ Installation failed: ${(err as Error).message}`);
      process.exit(1);
    }
  });

// ── backends ────────────────────────────────────────────────────────────────
program
  .command('backends')
  .description('List all registered backends')
  .action(() => {
    const backends = registry.listAll();
    for (const b of backends) {
      console.log(`${b.id} — ${b.name} (${b.license})`);
      console.log(`  ${b.description}`);
      console.log(`  ${b.url}`);
      console.log('');
    }
  });

// ── mcp ─────────────────────────────────────────────────────────────────────
const mcp = program
  .command('mcp')
  .description('Manage MCP servers');

mcp
  .command('add')
  .description('Register an MCP server')
  .argument('<name>', 'Server name')
  .argument('<command>', 'Server command')
  .argument('[args...]', 'Server arguments')
  .action(async (name: string, command: string, args: string[]) => {
    const adapter = new AgentAdapter();
    await adapter.mcpAdd({ name, command, args: args.length > 0 ? args : undefined });
  });

mcp
  .command('remove')
  .description('Remove an MCP server')
  .argument('<name>', 'Server name')
  .action(async (name: string) => {
    const adapter = new AgentAdapter();
    await adapter.mcpRemove(name);
  });

mcp
  .command('list')
  .description('List registered MCP servers')
  .action(async () => {
    const adapter = new AgentAdapter();
    const servers = await adapter.mcpList();
    if (servers.length === 0) {
      console.log('No MCP servers registered');
      return;
    }
    for (const s of servers) {
      console.log(`  ${s.name}: ${s.command} ${s.args?.join(' ') ?? ''}`);
    }
  });

// ── version ─────────────────────────────────────────────────────────────────
program
  .command('agent-version')
  .description('Show the active agent version')
  .action(async () => {
    const adapter = new AgentAdapter();
    const ver = await adapter.version();
    console.log(ver ?? 'not installed');
  });

// ── resolve-model ───────────────────────────────────────────────────────────
program
  .command('resolve-model')
  .description('Resolve a model tier name to a backend-specific model string')
  .argument('<model>', 'Model tier (opus/sonnet/haiku) or backend-specific string')
  .option('-b, --backend <backend>', 'Backend to resolve for')
  .action((model: string, opts) => {
    const adapter = new AgentAdapter(opts.backend);
    console.log(adapter.resolveModel(model));
  });

// ── Run ─────────────────────────────────────────────────────────────────────
program.parseAsync(process.argv).catch((err) => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});
