"""Tests for AgentScope main functionality."""

import pytest
from datetime import datetime

from agentscope import AgentScope
from agentscope.core.metrics import StepType
from agentscope.core.exceptions import AgentScopeError


class TestAgentScopeBasic:
    """Test basic AgentScope functionality."""

    def test_context_manager(self, mock_agent):
        """Test AgentScope as context manager."""
        with AgentScope(mock_agent) as scope:
            result = mock_agent.run("test input")
            assert result == "Processed: test input"

        assert scope.metrics.success is True
        assert scope.metrics.end_time is not None

    def test_metrics_initialization(self, mock_agent):
        """Test metrics are properly initialized."""
        with AgentScope(mock_agent, project="test") as scope:
            mock_agent.run("test")

        assert scope.metrics.project == "test"
        assert scope.metrics.start_time is not None
        assert scope.metrics.duration_ms > 0

    def test_with_tags(self, mock_agent):
        """Test AgentScope with tags."""
        tags = ["production", "critical"]
        with AgentScope(mock_agent, tags=tags) as scope:
            mock_agent.run("test")

        assert scope.metrics.tags == tags

    def test_verbose_mode(self, mock_agent, capsys):
        """Test verbose mode prints output."""
        with AgentScope(mock_agent, verbose=True) as scope:
            mock_agent.run("test")

        captured = capsys.readouterr()
        assert "AgentScope" in captured.out or len(captured.out) > 0


class TestAgentScopeMetrics:
    """Test metrics tracking."""

    def test_cost_tracking(self, mock_agent):
        """Test cost is tracked."""
        with AgentScope(mock_agent) as scope:
            # Log a step with cost
            scope.log_step(
                StepType.THOUGHT,
                "Thinking...",
                tokens=100,
                model="gpt-3.5-turbo"
            )

        assert scope.cost > 0
        assert scope.tokens > 0

    def test_token_counting(self, mock_agent):
        """Test token counting."""
        with AgentScope(mock_agent) as scope:
            scope.log_step(StepType.THOUGHT, "Step 1", tokens=50)
            scope.log_step(StepType.DECISION, "Step 2", tokens=75)

        assert scope.tokens == 125

    def test_tool_call_tracking(self, mock_agent):
        """Test tool calls are tracked."""
        with AgentScope(mock_agent) as scope:
            scope.log_step(
                StepType.TOOL_CALL,
                "Calling search tool",
                metadata={"tool_name": "search", "success": True}
            )
            scope.log_step(
                StepType.TOOL_CALL,
                "Calling search tool again",
                metadata={"tool_name": "search", "success": True}
            )

        assert "search" in scope.tool_calls
        assert scope.tool_calls["search"] == 2
        assert scope.total_tool_calls == 2

    def test_duration_tracking(self, mock_agent):
        """Test execution duration is tracked."""
        import time

        with AgentScope(mock_agent) as scope:
            time.sleep(0.1)  # Sleep for 100ms
            mock_agent.run("test")

        assert scope.duration_seconds >= 0.1
        assert scope.metrics.duration_ms >= 100


class TestAgentScopeErrorHandling:
    """Test error handling."""

    def test_agent_failure_captured(self, failing_agent):
        """Test that agent failures are captured."""
        with pytest.raises(ValueError):
            with AgentScope(failing_agent) as scope:
                failing_agent.run("test")

        assert scope.metrics.success is False
        assert scope.metrics.error is not None
        assert "Mock agent failed" in scope.metrics.error

    def test_cost_threshold_warning(self, mock_agent, capsys):
        """Test cost threshold warning."""
        with AgentScope(mock_agent, cost_threshold=0.001, verbose=True) as scope:
            # Log expensive step
            scope.log_step(
                StepType.THOUGHT,
                "Expensive operation",
                tokens=10000,
                model="gpt-4"
            )

        captured = capsys.readouterr()
        # Should warn about exceeding threshold
        assert "threshold" in captured.out.lower() or "cost" in captured.out.lower()


class TestAgentScopeExport:
    """Test export functionality."""

    def test_export_to_json(self, mock_agent, tmp_path):
        """Test exporting trace to JSON."""
        export_file = tmp_path / "trace.json"

        with AgentScope(mock_agent) as scope:
            scope.log_step(StepType.THOUGHT, "Test step")
            mock_agent.run("test")

        scope.export(str(export_file))

        assert export_file.exists()

        # Verify JSON is valid
        import json
        with open(export_file) as f:
            data = json.load(f)

        assert "metrics" in data
        assert "input" in data
        assert "steps" in data

    def test_export_with_verbose(self, mock_agent, tmp_path, capsys):
        """Test export with verbose output."""
        export_file = tmp_path / "trace.json"

        with AgentScope(mock_agent, verbose=True) as scope:
            mock_agent.run("test")

        scope.export(str(export_file))

        captured = capsys.readouterr()
        assert "Exported" in captured.out or str(export_file) in captured.out


class TestAgentScopeComparison:
    """Test comparison functionality."""

    def test_compare_multiple_scopes(self, mock_agent, capsys):
        """Test comparing multiple agent executions."""
        scopes = []

        for i in range(3):
            with AgentScope(mock_agent, name=f"agent_v{i+1}") as scope:
                scope.log_step(StepType.THOUGHT, f"Thought {i}", tokens=50 * (i+1))
                mock_agent.run(f"test {i}")
                scopes.append(scope)

        AgentScope.compare(scopes)

        captured = capsys.readouterr()
        assert "Comparison" in captured.out or "agent_v" in captured.out


class TestAgentScopeProperties:
    """Test AgentScope properties."""

    def test_cost_property(self, mock_agent):
        """Test cost property."""
        with AgentScope(mock_agent) as scope:
            scope.log_step(StepType.THOUGHT, "test", tokens=100, model="gpt-3.5-turbo")

        assert isinstance(scope.cost, float)
        assert scope.cost > 0

    def test_tokens_property(self, mock_agent):
        """Test tokens property."""
        with AgentScope(mock_agent) as scope:
            scope.log_step(StepType.THOUGHT, "test", tokens=100)

        assert isinstance(scope.tokens, int)
        assert scope.tokens == 100

    def test_tool_calls_property(self, mock_agent):
        """Test tool_calls property."""
        with AgentScope(mock_agent) as scope:
            scope.log_step(
                StepType.TOOL_CALL,
                "test",
                metadata={"tool_name": "search", "success": True}
            )

        assert isinstance(scope.tool_calls, dict)
        assert "search" in scope.tool_calls

    def test_duration_seconds_property(self, mock_agent):
        """Test duration_seconds property."""
        with AgentScope(mock_agent) as scope:
            mock_agent.run("test")

        assert isinstance(scope.duration_seconds, float)
        assert scope.duration_seconds > 0


class TestAgentScopePrintSummary:
    """Test summary printing."""

    def test_print_summary(self, mock_agent, capsys):
        """Test print_summary outputs correctly."""
        with AgentScope(mock_agent) as scope:
            scope.log_step(StepType.THOUGHT, "Thinking", tokens=50)
            scope.log_step(
                StepType.TOOL_CALL,
                "Search",
                metadata={"tool_name": "search", "success": True}
            )
            mock_agent.run("test")

        scope.print_summary()

        captured = capsys.readouterr()
        assert "Summary" in captured.out
        assert "Cost" in captured.out or "$" in captured.out
        assert "Tokens" in captured.out

    def test_print_summary_with_errors(self, failing_agent, capsys):
        """Test print_summary with failed execution."""
        with pytest.raises(ValueError):
            with AgentScope(failing_agent) as scope:
                failing_agent.run("test")

        scope.print_summary()

        captured = capsys.readouterr()
        assert "Failed" in captured.out or "✗" in captured.out
