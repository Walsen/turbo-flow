"""
OTEL observability for TurboFlow Strands agents.

Wires Strands' built-in OpenTelemetry instrumentation to exporters
(console, OTLP/CloudWatch, JSON file) and adds TurboFlow-specific
metrics: cost per task, tokens per agent type, team execution time.

Usage:
    from turboflow_adapter.strands.observability import setup_telemetry, track_execution

    # Enable console tracing (dev)
    setup_telemetry(console=True)

    # Enable OTLP export (production — CloudWatch, Jaeger, etc.)
    setup_telemetry(otlp=True, endpoint="http://localhost:4317")

    # Track a task execution with cost metrics
    with track_execution("coder", "implement login") as tracker:
        result = agent("implement login")
        tracker.record_result(result)
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Generator

from turboflow_adapter.logger import get_logger

log = get_logger("tf-adapter.strands.otel")

# ── Strands telemetry setup ──────────────────────────────────────────────

_telemetry_initialized = False


def setup_telemetry(
    console: bool = False,
    otlp: bool = False,
    endpoint: str | None = None,
    metrics: bool = True,
) -> None:
    """
    Initialize OTEL telemetry for Strands agents.

    Args:
        console: Enable console span exporter (for development/debugging)
        otlp: Enable OTLP exporter (for CloudWatch, Jaeger, Grafana, etc.)
        endpoint: OTLP endpoint URL (default: http://localhost:4317)
        metrics: Enable metrics collection (console or OTLP based on other flags)
    """
    global _telemetry_initialized
    if _telemetry_initialized:
        log.debug("Telemetry already initialized")
        return

    try:
        from strands.telemetry import StrandsTelemetry

        telemetry = StrandsTelemetry()

        if console:
            telemetry.setup_console_exporter()
            log.info("OTEL console exporter enabled")

        if otlp:
            kwargs: dict[str, Any] = {}
            if endpoint:
                kwargs["endpoint"] = endpoint
            elif ep := os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
                kwargs["endpoint"] = ep
            telemetry.setup_otlp_exporter(**kwargs)
            log.info("OTEL OTLP exporter enabled (endpoint: %s)", kwargs.get("endpoint", "default"))

        if metrics:
            telemetry.setup_meter(
                enable_console_exporter=console,
                enable_otlp_exporter=otlp,
            )
            log.info("OTEL metrics enabled")

        _telemetry_initialized = True

    except ImportError:
        log.warning("Strands telemetry not available — OTEL disabled")
    except Exception as e:
        log.warning("Failed to initialize telemetry: %s", e)


# ── Cost estimation ──────────────────────────────────────────────────────

# Bedrock pricing per 1M tokens (April 2026 estimates)
_COST_PER_M_TOKENS: dict[str, dict[str, float]] = {
    "opus": {"input": 5.0, "output": 25.0},
    "sonnet": {"input": 3.0, "output": 15.0},
    "haiku": {"input": 0.80, "output": 4.0},
}


def estimate_cost(model_tier: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost in USD for a given token usage."""
    tier = model_tier.lower()
    # Normalize tier names
    for key in _COST_PER_M_TOKENS:
        if key in tier:
            tier = key
            break
    else:
        tier = "sonnet"  # default

    rates = _COST_PER_M_TOKENS[tier]
    cost = (input_tokens / 1_000_000) * rates["input"] + (output_tokens / 1_000_000) * rates[
        "output"
    ]
    return round(cost, 6)


# ── Execution tracking ───────────────────────────────────────────────────


@dataclass
class ExecutionMetrics:
    """Metrics collected during a single agent or team execution."""

    agent_type: str
    task_summary: str
    model_tier: str = "unknown"
    start_time: float = 0.0
    end_time: float = 0.0
    duration_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    tool_calls: int = 0
    estimated_cost_usd: float = 0.0
    success: bool = True
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_type": self.agent_type,
            "task_summary": self.task_summary[:100],
            "model_tier": self.model_tier,
            "duration_ms": round(self.duration_ms, 2),
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "tool_calls": self.tool_calls,
            "estimated_cost_usd": self.estimated_cost_usd,
            "success": self.success,
            "error": self.error,
        }

    def summary(self) -> str:
        return (
            f"[{self.agent_type}] {self.task_summary[:50]}... "
            f"| {self.duration_ms:.0f}ms "
            f"| {self.total_tokens} tokens "
            f"| ${self.estimated_cost_usd:.4f} "
            f"| {'✓' if self.success else '✗'}"
        )


class ExecutionTracker:
    """Context manager that tracks execution metrics for an agent invocation."""

    def __init__(self, agent_type: str, task: str, model_tier: str = "unknown") -> None:
        self.metrics = ExecutionMetrics(
            agent_type=agent_type,
            task_summary=task,
            model_tier=model_tier,
        )

    def record_result(self, result: Any) -> None:
        """Extract metrics from a Strands AgentResult."""
        try:
            # Strands AgentResult has metrics in the event loop
            if hasattr(result, "metrics"):
                m = result.metrics
                if hasattr(m, "input_tokens"):
                    self.metrics.input_tokens = m.input_tokens
                if hasattr(m, "output_tokens"):
                    self.metrics.output_tokens = m.output_tokens
                if hasattr(m, "total_tokens"):
                    self.metrics.total_tokens = m.total_tokens

            # Try to get token counts from the result's message history
            if hasattr(result, "messages"):
                for msg in result.messages:
                    if hasattr(msg, "usage"):
                        usage = msg.usage
                        self.metrics.input_tokens += getattr(usage, "input_tokens", 0)
                        self.metrics.output_tokens += getattr(usage, "output_tokens", 0)

            self.metrics.total_tokens = self.metrics.input_tokens + self.metrics.output_tokens
            self.metrics.estimated_cost_usd = estimate_cost(
                self.metrics.model_tier,
                self.metrics.input_tokens,
                self.metrics.output_tokens,
            )
        except Exception as e:
            log.debug("Could not extract metrics from result: %s", e)

    def record_error(self, error: str) -> None:
        self.metrics.success = False
        self.metrics.error = error


@contextmanager
def track_execution(
    agent_type: str,
    task: str,
    model_tier: str = "unknown",
) -> Generator[ExecutionTracker, None, None]:
    """
    Context manager to track agent execution metrics.

    Usage:
        with track_execution("coder", "implement login", "sonnet") as tracker:
            result = agent("implement login")
            tracker.record_result(result)
        print(tracker.metrics.summary())
    """
    tracker = ExecutionTracker(agent_type, task, model_tier)
    tracker.metrics.start_time = time.monotonic()

    try:
        yield tracker
    except Exception as e:
        tracker.record_error(str(e))
        raise
    finally:
        tracker.metrics.end_time = time.monotonic()
        tracker.metrics.duration_ms = (tracker.metrics.end_time - tracker.metrics.start_time) * 1000
        log.info(tracker.metrics.summary())
