// =============================================================================
// TurboFlow Agent Adapter — Process Runner
//
// Wraps child_process.spawn with timeout, streaming, and structured results.
// =============================================================================

import { spawn } from 'node:child_process';
import type { ExecResult } from './types.js';
import { Logger } from './logger.js';

const log = new Logger('process');

export interface RunOptions {
  /** Command to execute */
  command: string;
  /** Arguments */
  args?: string[];
  /** Working directory */
  cwd?: string;
  /** Environment variables (merged with process.env) */
  env?: Record<string, string>;
  /** Timeout in ms (0 = no timeout) */
  timeout?: number;
  /** Pipe stdin from this string */
  stdin?: string;
  /** Stream stdout to process.stdout in real-time */
  stream?: boolean;
}

export function run(options: RunOptions): Promise<ExecResult> {
  const { command, args = [], cwd, env, timeout = 0, stdin, stream = false } = options;
  const startTime = Date.now();

  log.debug(`Spawning: ${command} ${args.join(' ')}`, { cwd, timeout });

  return new Promise((resolve) => {
    const proc = spawn(command, args, {
      cwd,
      env: { ...process.env, ...env },
      stdio: ['pipe', 'pipe', 'pipe'],
      shell: false,
    });

    const stdoutChunks: Buffer[] = [];
    const stderrChunks: Buffer[] = [];
    let timedOut = false;
    let timer: ReturnType<typeof setTimeout> | undefined;

    if (timeout > 0) {
      timer = setTimeout(() => {
        timedOut = true;
        proc.kill('SIGTERM');
        // Force kill after 5s if SIGTERM doesn't work
        setTimeout(() => proc.kill('SIGKILL'), 5000);
      }, timeout);
    }

    proc.stdout.on('data', (chunk: Buffer) => {
      stdoutChunks.push(chunk);
      if (stream) {
        process.stdout.write(chunk);
      }
    });

    proc.stderr.on('data', (chunk: Buffer) => {
      stderrChunks.push(chunk);
      if (stream) {
        process.stderr.write(chunk);
      }
    });

    if (stdin) {
      proc.stdin.write(stdin);
      proc.stdin.end();
    } else {
      proc.stdin.end();
    }

    proc.on('close', (code) => {
      if (timer) clearTimeout(timer);
      const durationMs = Date.now() - startTime;

      const result: ExecResult = {
        exitCode: code ?? 1,
        stdout: Buffer.concat(stdoutChunks).toString('utf-8'),
        stderr: Buffer.concat(stderrChunks).toString('utf-8'),
        durationMs,
        timedOut,
      };

      log.debug(`Process exited`, { exitCode: result.exitCode, durationMs, timedOut });
      resolve(result);
    });

    proc.on('error', (err) => {
      if (timer) clearTimeout(timer);
      const durationMs = Date.now() - startTime;

      resolve({
        exitCode: 1,
        stdout: Buffer.concat(stdoutChunks).toString('utf-8'),
        stderr: err.message,
        durationMs,
        timedOut: false,
      });
    });
  });
}

/** Check if a command exists on PATH */
export async function commandExists(cmd: string): Promise<boolean> {
  const result = await run({
    command: process.platform === 'win32' ? 'where' : 'which',
    args: [cmd],
    timeout: 5000,
  });
  return result.exitCode === 0;
}
