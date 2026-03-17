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
)


def test_token_usage_add():
    """Test token usage addition."""
    usage = TokenUsage()
    usage.add(100, 50)
    
    assert usage.prompt_tokens == 100
    assert usage.completion_tokens == 50
    assert usage.total_tokens == 150
    
    usage.add(200, 75)
    assert usage.total_tokens == 425


def test_cost_breakdown_add():
    """Test cost breakdown addition."""
    breakdown = CostBreakdown()
    breakdown.add("gpt-4", "completion", 0.005)
    breakdown.add("gpt-4", "completion", 0.003)
    breakdown.add("gpt-3.5-turbo", "completion", 0.001)
    
    assert breakdown.total == pytest.approx(0.009)
    assert breakdown.by_model["gpt-4"] == pytest.approx(0.008)
    assert breakdown.by_model["gpt-3.5-turbo"] == pytest.approx(0.001)


def test_tool_call_stats():
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


def test_metrics_add_step():
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


def test_metrics_tool_call_tracking():
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


def test_metrics_to_dict():
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
