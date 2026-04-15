// =============================================================================
// TurboFlow Agent Adapter — Error Types
// =============================================================================

/** Base error for all adapter errors */
export class AdapterError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly cause?: Error,
  ) {
    super(message);
    this.name = 'AdapterError';
  }
}

/** Backend is not installed */
export class BackendNotInstalledError extends AdapterError {
  constructor(public readonly backend: string) {
    super(
      `Backend '${backend}' is not installed. Run: tf-adapter install ${backend}`,
      'BACKEND_NOT_INSTALLED',
    );
    this.name = 'BackendNotInstalledError';
  }
}

/** Unknown backend identifier */
export class UnknownBackendError extends AdapterError {
  constructor(
    public readonly backend: string,
    public readonly supported: string[],
  ) {
    super(
      `Unknown backend '${backend}'. Supported: ${supported.join(', ')}`,
      'UNKNOWN_BACKEND',
    );
    this.name = 'UnknownBackendError';
  }
}

/** Backend doesn't support the requested capability */
export class CapabilityNotSupportedError extends AdapterError {
  constructor(
    public readonly backend: string,
    public readonly capability: string,
  ) {
    super(
      `Backend '${backend}' does not support '${capability}'`,
      'CAPABILITY_NOT_SUPPORTED',
    );
    this.name = 'CapabilityNotSupportedError';
  }
}

/** Agent execution failed */
export class ExecError extends AdapterError {
  constructor(
    message: string,
    public readonly exitCode: number,
    public readonly stderr: string,
    cause?: Error,
  ) {
    super(message, 'EXEC_FAILED', cause);
    this.name = 'ExecError';
  }
}

/** Agent execution timed out */
export class TimeoutError extends AdapterError {
  constructor(
    public readonly timeoutMs: number,
  ) {
    super(
      `Agent execution timed out after ${timeoutMs}ms`,
      'EXEC_TIMEOUT',
    );
    this.name = 'TimeoutError';
  }
}

/** Configuration error */
export class ConfigError extends AdapterError {
  constructor(message: string, cause?: Error) {
    super(message, 'CONFIG_ERROR', cause);
    this.name = 'ConfigError';
  }
}
