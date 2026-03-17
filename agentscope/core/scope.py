"""Core AgentScope monitoring class."""

import time
from datetime import datetime
from typing import Any, Optional, List, Dict
from contextlib import contextmanager

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from agentscope.core.metrics import Metrics, ExecutionTrace, ExecutionStep, StepType
from agentscope.core.pricing import PricingCalculator
from agentscope.core.exceptions import AgentScopeError
from agentscope.adapters.base import BaseAdapter
from agentscope.adapters.langchain_adapter import LangChainAdapter


class AgentScope:
    """
    Main monitoring context for AI agents.
    
    Usage:
        with AgentScope(agent, project="my-app") as scope:
            result = agent.run("task")
        
        print(f"Cost: ${scope.cost}")
        scope.print_summary()
    """

    def __init__(
        self,
        agent: Any,
        project: Optional[str] = None,
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        verbose: bool = False,
        cost_threshold: Optional[float] = None,
    ):
        """
        Initialize AgentScope.
        
        Args:
            agent: The agent instance to monitor
            project: Project name for organization
            name: Human-readable name for this scope
            tags: Tags for filtering/grouping
            verbose: Print live updates
            cost_threshold: Alert if cost exceeds this value
        """
        self.agent = agent
        self.project = project
        self.name = name or "agent"
        self.tags = tags or []
        self.verbose = verbose
        self.cost_threshold = cost_threshold

        # Initialize metrics
        self.metrics = Metrics(
            start_time=datetime.now(),
            project=project,
            tags=tags,
            agent_name=name,
        )

        # Components
        self.console = Console() if verbose else None
        self.pricing = PricingCalculator()
        self.adapter: Optional[BaseAdapter] = None

        # Execution tracking
        self._input: Optional[str] = None
        self._output: Optional[str] = None
        self._intermediate_steps: List[Dict[str, Any]] = []

    def __enter__(self) -> "AgentScope":
        """Enter context manager."""
        self._start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Exit context manager."""
        if exc_type is not None:
            self.metrics.success = False
            self.metrics.error = str(exc_val)
        else:
            self.metrics.success = True

        self._finish()
        return False  # Don't suppress exceptions

    def _start(self) -> None:
        """Start monitoring."""
        self.metrics.start_time = datetime.now()

        # Detect and wrap agent
        self.adapter = self._detect_adapter()
        if self.adapter:
            self.adapter.wrap(self.agent, self)

        if self.verbose:
            self.console.print(
                Panel(
                    f"[bold cyan]AgentScope Started[/]\n"
                    f"Project: {self.project or 'None'}\n"
                    f"Agent: {self.name}",
                    border_style="cyan",
                )
            )

    def _finish(self) -> None:
        """Finish monitoring."""
        self.metrics.end_time = datetime.now()
        self.metrics.duration_ms = int(
            (self.metrics.end_time - self.metrics.start_time).total_seconds() * 1000
        )

        # Check cost threshold
        if self.cost_threshold and self.cost > self.cost_threshold:
            if self.console:
                self.console.print(
                    f"[bold red]⚠️  Cost threshold exceeded: "
                    f"${self.cost:.4f} > ${self.cost_threshold:.4f}[/]"
                )

        if self.verbose:
            self.print_summary()

    def _detect_adapter(self) -> Optional[BaseAdapter]:
        """Auto-detect agent framework."""
        agent_type = type(self.agent).__name__
        module = type(self.agent).__module__

        if "langchain" in module.lower():
            return LangChainAdapter()

        # Future: CrewAI, AutoGen adapters
        return None

    def log_step(
        self,
        step_type: StepType,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        tokens: int = 0,
        model: Optional[str] = None,
    ) -> None:
        """Log an execution step."""
        start = time.time()

        # Calculate cost if model provided
        cost = 0.0
        if model and tokens > 0:
            cost = self.pricing.calculate(model, prompt_tokens=tokens, completion_tokens=0)

        step = ExecutionStep(
            timestamp=datetime.now(),
            step_type=step_type,
            content=content,
            metadata=metadata or {},
            tokens=tokens,
            cost=cost,
            duration_ms=int((time.time() - start) * 1000),
        )

        self.metrics.add_step(step)

        if self.verbose and self.console:
            self._print_step(step)

    def _print_step(self, step: ExecutionStep) -> None:
        """Print step to console."""
        icon = {
            StepType.THOUGHT: "💭",
            StepType.TOOL_CALL: "🔧",
            StepType.OBSERVATION: "👀",
            StepType.DECISION: "🎯",
            StepType.ERROR: "❌",
        }.get(step.step_type, "•")

        self.console.print(f"{icon} [{step.step_type.value}] {step.content[:100]}")

    def print_summary(self) -> None:
        """Print execution summary."""
        console = self.console or Console()

        # Create summary table
        table = Table(title="AgentScope Execution Summary", box=box.ROUNDED, show_header=False)
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        # Status
        status = "✓ Success" if self.metrics.success else f"✗ Failed: {self.metrics.error}"
        table.add_row("Status", status)

        # Timing
        table.add_row("Duration", f"{self.metrics.duration_seconds:.2f}s")

        # Cost & Tokens
        table.add_row("Cost", f"${self.cost:.4f}")
        table.add_row(
            "Tokens",
            f"{self.metrics.tokens.prompt_tokens} (prompt) + "
            f"{self.metrics.tokens.completion_tokens} (completion)",
        )

        # Tools
        if self.metrics.tool_calls:
            tool_summary = "\n".join(
                f"  - {name}: {stats.call_count}x"
                for name, stats in self.metrics.tool_calls.items()
            )
            table.add_row("Tools", f"{self.total_tool_calls} calls\n{tool_summary}")

        # Decisions
        table.add_row("Decisions", str(self.metrics.decision_count))

        console.print(table)

    @property
    def cost(self) -> float:
        """Total execution cost."""
        return self.metrics.cost.total

    @property
    def tokens(self) -> int:
        """Total tokens used."""
        return self.metrics.tokens.total_tokens

    @property
    def tool_calls(self) -> Dict[str, int]:
        """Tool call counts."""
        return {name: stats.call_count for name, stats in self.metrics.tool_calls.items()}

    @property
    def total_tool_calls(self) -> int:
        """Total number of tool calls."""
        return self.metrics.total_tool_calls

    @property
    def duration_seconds(self) -> float:
        """Duration in seconds."""
        return self.metrics.duration_seconds

    def export(self, filepath: str) -> None:
        """
        Export execution trace to file.
        
        Args:
            filepath: Output file path (supports .json, .yaml)
        """
        import json

        trace = ExecutionTrace(
            metrics=self.metrics,
            steps=self.metrics.steps,
            input=self._input or "",
            output=self._output,
            intermediate_steps=self._intermediate_steps,
        )

        with open(filepath, "w") as f:
            json.dump(trace.to_dict(), f, indent=2)

        if self.console:
            self.console.print(f"[green]✓ Exported to {filepath}[/]")

    @staticmethod
    def load(filepath: str) -> ExecutionTrace:
        """Load execution trace from file."""
        import json

        with open(filepath) as f:
            data = json.load(f)

        # TODO: Reconstruct ExecutionTrace from dict
        return data

    @staticmethod
    def compare(scopes: List["AgentScope"]) -> None:
        """Compare multiple agent executions."""
        console = Console()

        table = Table(title="Agent Comparison", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")

        for scope in scopes:
            table.add_column(scope.name, style="green")

        # Add comparison rows
        metrics = [
            ("Duration", lambda s: f"{s.duration_seconds:.2f}s"),
            ("Cost", lambda s: f"${s.cost:.4f}"),
            ("Tokens", lambda s: str(s.tokens)),
            ("Tool Calls", lambda s: str(s.total_tool_calls)),
            ("Success", lambda s: "✓" if s.metrics.success else "✗"),
        ]

        for name, getter in metrics:
            table.add_row(name, *[getter(scope) for scope in scopes])

        console.print(table)
