// =============================================================================
// TurboFlow Agent Adapter — Logger
// =============================================================================

import type { LogLevel } from './types.js';

const LEVEL_ORDER: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

const LEVEL_COLORS: Record<LogLevel, string> = {
  debug: '\x1b[90m',  // gray
  info: '\x1b[36m',   // cyan
  warn: '\x1b[33m',   // yellow
  error: '\x1b[31m',  // red
};

const RESET = '\x1b[0m';

export class Logger {
  private level: LogLevel;
  private prefix: string;

  constructor(prefix = 'tf-adapter', level?: LogLevel) {
    this.prefix = prefix;
    this.level = level ?? (process.env.TF_ADAPTER_LOG_LEVEL as LogLevel) ?? 'info';
  }

  private shouldLog(level: LogLevel): boolean {
    return LEVEL_ORDER[level] >= LEVEL_ORDER[this.level];
  }

  private format(level: LogLevel, message: string, meta?: Record<string, unknown>): string {
    const color = LEVEL_COLORS[level];
    const ts = new Date().toISOString().slice(11, 23);
    const metaStr = meta ? ` ${JSON.stringify(meta)}` : '';
    return `${color}[${ts}] [${this.prefix}] ${level.toUpperCase()}${RESET} ${message}${metaStr}`;
  }

  debug(message: string, meta?: Record<string, unknown>): void {
    if (this.shouldLog('debug')) {
      console.debug(this.format('debug', message, meta));
    }
  }

  info(message: string, meta?: Record<string, unknown>): void {
    if (this.shouldLog('info')) {
      console.info(this.format('info', message, meta));
    }
  }

  warn(message: string, meta?: Record<string, unknown>): void {
    if (this.shouldLog('warn')) {
      console.warn(this.format('warn', message, meta));
    }
  }

  error(message: string, meta?: Record<string, unknown>): void {
    if (this.shouldLog('error')) {
      console.error(this.format('error', message, meta));
    }
  }

  child(prefix: string): Logger {
    return new Logger(`${this.prefix}:${prefix}`, this.level);
  }
}

export const logger = new Logger();
