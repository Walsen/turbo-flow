"""Tests for OTEL observability module."""

from turboflow_adapter.strands.observability import (
    estimate_cost,
    track_execution,
    ExecutionMetrics,
)


class TestEstimateCost:
    def test_haiku_cheap(self) -> None:
        cost = estimate_cost("haiku", input_tokens=1000, output_tokens=500)
        assert cost < 0.01

    def test_opus_expensive(self) -> None:
        cost = estimate_cost("opus", input_tokens=1_000_000, output_tokens=500_000)
        assert cost > 10.0

    def test_sonnet_middle(self) -> None:
        cost = estimate_cost("sonnet", input_tokens=100_000, output_tokens=50_000)
        assert 0.1 < cost < 5.0

    def test_unknown_tier_defaults_to_sonnet(self) -> None:
        cost_unknown = estimate_cost("unknown-model", input_tokens=1000, output_tokens=500)
        cost_sonnet = estimate_cost("sonnet", input_tokens=1000, output_tokens=500)
        assert cost_unknown == cost_sonnet

    def test_zero_tokens(self) -> None:
        cost = estimate_cost("opus", input_tokens=0, output_tokens=0)
        assert cost == 0.0

    def test_bedrock_model_id_resolves(self) -> None:
        # Model IDs containing tier names should resolve
        cost = estimate_cost("us.anthropic.claude-haiku-4-5", input_tokens=1000, output_tokens=500)
        cost_haiku = estimate_cost("haiku", input_tokens=1000, output_tokens=500)
        assert cost == cost_haiku


class TestTrackExecution:
    def test_tracks_duration(self) -> None:
        import time

        with track_execution("coder", "test task", "sonnet") as tracker:
            time.sleep(0.05)  # 50ms

        assert tracker.metrics.duration_ms >= 40  # allow some slack
        assert tracker.metrics.agent_type == "coder"
        assert tracker.metrics.task_summary == "test task"

    def test_records_error(self) -> None:
        try:
            with track_execution("coder", "failing task") as tracker:
                raise ValueError("test error")
        except ValueError:
            pass

        assert tracker.metrics.success is False
        assert tracker.metrics.error == "test error"

    def test_summary_format(self) -> None:
        metrics = ExecutionMetrics(
            agent_type="coder",
            task_summary="implement login feature",
            model_tier="sonnet",
            duration_ms=1500.0,
            total_tokens=5000,
            estimated_cost_usd=0.0225,
            success=True,
        )
        summary = metrics.summary()
        assert "coder" in summary
        assert "1500ms" in summary
        assert "5000 tokens" in summary
        assert "$0.0225" in summary
        assert "✓" in summary

    def test_to_dict(self) -> None:
        metrics = ExecutionMetrics(
            agent_type="tester",
            task_summary="write tests",
            model_tier="haiku",
            duration_ms=800.0,
            input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
            estimated_cost_usd=0.003,
            success=True,
        )
        d = metrics.to_dict()
        assert d["agent_type"] == "tester"
        assert d["model_tier"] == "haiku"
        assert d["total_tokens"] == 1500
        assert d["success"] is True
