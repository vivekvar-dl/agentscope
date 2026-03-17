"""Metrics tracking and calculation."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class StepType(Enum):
    """Type of execution step."""

    THOUGHT = "thought"
    TOOL_CALL = "tool_call"
    OBSERVATION = "observation"
    DECISION = "decision"
    ERROR = "error"


@dataclass
class ExecutionStep:
    """Single step in agent execution."""

    timestamp: datetime
    step_type: StepType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    tokens: int = 0
    cost: float = 0.0
    duration_ms: int = 0


@dataclass
class TokenUsage:
    """Token usage breakdown."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def add(self, prompt: int, completion: int) -> None:
        """Add tokens to usage."""
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        self.total_tokens += prompt + completion


@dataclass
class CostBreakdown:
    """Cost breakdown by model and operation."""

    total: float = 0.0
    by_model: Dict[str, float] = field(default_factory=dict)
    by_operation: Dict[str, float] = field(default_factory=dict)

    def add(self, model: str, operation: str, cost: float) -> None:
        """Add cost to breakdown."""
        self.total += cost
        self.by_model[model] = self.by_model.get(model, 0.0) + cost
        self.by_operation[operation] = self.by_operation.get(operation, 0.0) + cost


@dataclass
class ToolCallStats:
    """Statistics for tool calls."""

    tool_name: str
    call_count: int = 0
    total_duration_ms: int = 0
    error_count: int = 0
    success_count: int = 0

    @property
    def avg_duration_ms(self) -> float:
        """Average duration per call."""
        return self.total_duration_ms / self.call_count if self.call_count > 0 else 0.0

    @property
    def success_rate(self) -> float:
        """Success rate as percentage."""
        total = self.success_count + self.error_count
        return (self.success_count / total * 100) if total > 0 else 0.0


@dataclass
class Metrics:
    """Complete metrics for an agent execution."""

    # Timing
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: int = 0

    # Status
    success: bool = False
    error: Optional[str] = None

    # Token & Cost
    tokens: TokenUsage = field(default_factory=TokenUsage)
    cost: CostBreakdown = field(default_factory=CostBreakdown)

    # Execution details
    steps: List[ExecutionStep] = field(default_factory=list)
    tool_calls: Dict[str, ToolCallStats] = field(default_factory=dict)
    decision_count: int = 0

    # Metadata
    project: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    agent_name: Optional[str] = None
    model: Optional[str] = None

    def add_step(self, step: ExecutionStep) -> None:
        """Add an execution step."""
        self.steps.append(step)

        # Update counters
        if step.step_type == StepType.DECISION:
            self.decision_count += 1
        elif step.step_type == StepType.TOOL_CALL:
            tool_name = step.metadata.get("tool_name", "unknown")
            if tool_name not in self.tool_calls:
                self.tool_calls[tool_name] = ToolCallStats(tool_name=tool_name)

            stats = self.tool_calls[tool_name]
            stats.call_count += 1
            stats.total_duration_ms += step.duration_ms

            if step.metadata.get("success", True):
                stats.success_count += 1
            else:
                stats.error_count += 1

        # Update tokens and cost
        self.tokens.total_tokens += step.tokens
        self.cost.total += step.cost

    @property
    def duration_seconds(self) -> float:
        """Duration in seconds."""
        return self.duration_ms / 1000.0

    @property
    def total_tool_calls(self) -> int:
        """Total number of tool calls."""
        return sum(stats.call_count for stats in self.tool_calls.values())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "duration_seconds": self.duration_seconds,
            "success": self.success,
            "error": self.error,
            "tokens": {
                "prompt": self.tokens.prompt_tokens,
                "completion": self.tokens.completion_tokens,
                "total": self.tokens.total_tokens,
            },
            "cost": {
                "total": self.cost.total,
                "by_model": self.cost.by_model,
                "by_operation": self.cost.by_operation,
            },
            "tool_calls": {
                name: {
                    "count": stats.call_count,
                    "avg_duration_ms": stats.avg_duration_ms,
                    "success_rate": stats.success_rate,
                }
                for name, stats in self.tool_calls.items()
            },
            "decisions": self.decision_count,
            "metadata": {
                "project": self.project,
                "tags": self.tags,
                "agent_name": self.agent_name,
                "model": self.model,
            },
        }


@dataclass
class ExecutionTrace:
    """Complete execution trace for replay."""

    metrics: Metrics
    steps: List[ExecutionStep]
    input: str
    output: Optional[str] = None
    intermediate_steps: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "metrics": self.metrics.to_dict(),
            "input": self.input,
            "output": self.output,
            "steps": [
                {
                    "timestamp": step.timestamp.isoformat(),
                    "type": step.step_type.value,
                    "content": step.content,
                    "metadata": step.metadata,
                    "tokens": step.tokens,
                    "cost": step.cost,
                    "duration_ms": step.duration_ms,
                }
                for step in self.steps
            ],
            "intermediate_steps": self.intermediate_steps,
        }
