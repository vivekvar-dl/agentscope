"""Tests for metrics module."""

from datetime import datetime
import pytest

from agentscope.core.metrics import (
    Metrics,
    TokenUsage,
    CostBreakdown,
    ExecutionStep,
    StepType,
    ToolCallStats,
    ExecutionTrace,
)


class TestTokenUsage:
    """Test TokenUsage class."""

    def test_token_usage_initialization(self):
        """Test token usage starts at zero."""
        usage = TokenUsage()
        
        assert usage.prompt_tokens == 0
        assert usage.completion_tokens == 0
        assert usage.total_tokens == 0

    def test_token_usage_add(self):
        """Test token usage addition."""
        usage = TokenUsage()
        usage.add(100, 50)
        
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150
        
        usage.add(200, 75)
        assert usage.total_tokens == 425

    def test_multiple_additions(self):
        """Test multiple token additions."""
        usage = TokenUsage()
        
        for i in range(10):
            usage.add(10, 5)
        
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150


class TestCostBreakdown:
    """Test CostBreakdown class."""

    def test_cost_breakdown_initialization(self):
        """Test cost breakdown starts at zero."""
        breakdown = CostBreakdown()
        
        assert breakdown.total == 0.0
        assert len(breakdown.by_model) == 0
        assert len(breakdown.by_operation) == 0

    def test_cost_breakdown_add(self):
        """Test cost breakdown addition."""
        breakdown = CostBreakdown()
        breakdown.add("gpt-4", "completion", 0.005)
        breakdown.add("gpt-4", "completion", 0.003)
        breakdown.add("gpt-3.5-turbo", "completion", 0.001)
        
        assert breakdown.total == pytest.approx(0.009)
        assert breakdown.by_model["gpt-4"] == pytest.approx(0.008)
        assert breakdown.by_model["gpt-3.5-turbo"] == pytest.approx(0.001)

    def test_cost_by_operation(self):
        """Test cost tracking by operation type."""
        breakdown = CostBreakdown()
        breakdown.add("gpt-4", "completion", 0.005)
        breakdown.add("gpt-4", "embedding", 0.002)
        
        assert breakdown.by_operation["completion"] == pytest.approx(0.005)
        assert breakdown.by_operation["embedding"] == pytest.approx(0.002)

    def test_multiple_models(self):
        """Test tracking costs for multiple models."""
        breakdown = CostBreakdown()
        models = ["gpt-4", "claude-3-sonnet", "gemini-pro"]
        
        for model in models:
            breakdown.add(model, "completion", 0.01)
        
        assert len(breakdown.by_model) == 3
        assert breakdown.total == pytest.approx(0.03)


class TestToolCallStats:
    """Test ToolCallStats class."""

    def test_tool_call_stats_initialization(self):
        """Test tool call stats initialization."""
        stats = ToolCallStats(tool_name="search")
        
        assert stats.tool_name == "search"
        assert stats.call_count == 0
        assert stats.total_duration_ms == 0
        assert stats.error_count == 0
        assert stats.success_count == 0

    def test_tool_call_stats(self):
        """Test tool call statistics."""
        stats = ToolCallStats(tool_name="search")
        assert stats.call_count == 0
        assert stats.success_rate == 0.0
        
        stats.call_count = 10
        stats.success_count = 8
        stats.error_count = 2
        stats.total_duration_ms = 5000
        
        assert stats.avg_duration_ms == 500.0
        assert stats.success_rate == 80.0

    def test_perfect_success_rate(self):
        """Test 100% success rate."""
        stats = ToolCallStats(tool_name="test")
        stats.call_count = 10
        stats.success_count = 10
        stats.error_count = 0
        
        assert stats.success_rate == 100.0

    def test_zero_calls(self):
        """Test stats with zero calls."""
        stats = ToolCallStats(tool_name="test")
        
        assert stats.avg_duration_ms == 0.0
        assert stats.success_rate == 0.0


class TestMetrics:
    """Test Metrics class."""

    def test_metrics_initialization(self):
        """Test metrics initialization."""
        metrics = Metrics(start_time=datetime.now())
        
        assert metrics.start_time is not None
        assert metrics.end_time is None
        assert metrics.success is False
        assert metrics.error is None
        assert len(metrics.steps) == 0

    def test_metrics_add_step(self):
        """Test adding execution steps to metrics."""
        metrics = Metrics(start_time=datetime.now())
        
        step1 = ExecutionStep(
            timestamp=datetime.now(),
            step_type=StepType.THOUGHT,
            content="Thinking...",
            tokens=50,
            cost=0.001,
        )
        
        metrics.add_step(step1)
        assert len(metrics.steps) == 1
        assert metrics.tokens.total_tokens == 50
        assert metrics.cost.total == 0.001

    def test_metrics_multiple_steps(self):
        """Test adding multiple execution steps."""
        metrics = Metrics(start_time=datetime.now())
        
        for i in range(5):
            step = ExecutionStep(
                timestamp=datetime.now(),
                step_type=StepType.THOUGHT,
                content=f"Step {i}",
                tokens=10,
                cost=0.001,
            )
            metrics.add_step(step)
        
        assert len(metrics.steps) == 5
        assert metrics.tokens.total_tokens == 50
        assert metrics.cost.total == pytest.approx(0.005)

    def test_metrics_tool_call_tracking(self):
        """Test tool call tracking in metrics."""
        metrics = Metrics(start_time=datetime.now())
        
        step = ExecutionStep(
            timestamp=datetime.now(),
            step_type=StepType.TOOL_CALL,
            content="Calling search tool",
            metadata={"tool_name": "search", "success": True},
            duration_ms=500,
        )
        
        metrics.add_step(step)
        
        assert "search" in metrics.tool_calls
        assert metrics.tool_calls["search"].call_count == 1
        assert metrics.tool_calls["search"].success_count == 1
        assert metrics.total_tool_calls == 1

    def test_metrics_decision_counting(self):
        """Test decision counting in metrics."""
        metrics = Metrics(start_time=datetime.now())
        
        for i in range(3):
            step = ExecutionStep(
                timestamp=datetime.now(),
                step_type=StepType.DECISION,
                content=f"Decision {i}",
            )
            metrics.add_step(step)
        
        assert metrics.decision_count == 3

    def test_metrics_duration_seconds(self):
        """Test duration_seconds property."""
        metrics = Metrics(start_time=datetime.now())
        metrics.duration_ms = 2500
        
        assert metrics.duration_seconds == 2.5

    def test_metrics_to_dict(self):
        """Test metrics serialization."""
        metrics = Metrics(
            start_time=datetime.now(),
            project="test",
            tags=["unit-test"],
        )
        metrics.end_time = datetime.now()
        metrics.duration_ms = 1000
        metrics.success = True
        
        data = metrics.to_dict()
        
        assert data["project"] == "test"
        assert data["success"] is True
        assert "tokens" in data
        assert "cost" in data
        assert "metadata" in data
        assert data["duration_seconds"] == 1.0


class TestExecutionTrace:
    """Test ExecutionTrace class."""

    def test_execution_trace_creation(self):
        """Test creating an execution trace."""
        metrics = Metrics(start_time=datetime.now())
        metrics.success = True
        
        trace = ExecutionTrace(
            metrics=metrics,
            steps=[],
            input="test input",
            output="test output"
        )
        
        assert trace.input == "test input"
        assert trace.output == "test output"
        assert trace.metrics.success is True

    def test_execution_trace_to_dict(self):
        """Test execution trace serialization."""
        metrics = Metrics(start_time=datetime.now())
        step = ExecutionStep(
            timestamp=datetime.now(),
            step_type=StepType.THOUGHT,
            content="test",
        )
        
        trace = ExecutionTrace(
            metrics=metrics,
            steps=[step],
            input="test input",
            output="test output"
        )
        
        data = trace.to_dict()
        
        assert "metrics" in data
        assert "input" in data
        assert "output" in data
        assert "steps" in data
        assert len(data["steps"]) == 1
