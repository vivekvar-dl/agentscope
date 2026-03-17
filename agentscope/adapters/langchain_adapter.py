"""LangChain adapter for AgentScope."""

from typing import Any, TYPE_CHECKING

from agentscope.adapters.base import BaseAdapter
from agentscope.core.metrics import StepType

if TYPE_CHECKING:
    from agentscope.core.scope import AgentScope


class LangChainAdapter(BaseAdapter):
    """Adapter for LangChain agents."""

    def wrap(self, agent: Any, scope: "AgentScope") -> None:
        """Wrap a LangChain agent."""
        # Store original methods
        agent._original_call = getattr(agent, "__call__", None)
        agent._original_run = getattr(agent, "run", None)
        agent._original_invoke = getattr(agent, "invoke", None)

        # Monkey-patch with monitoring
        def monitored_call(*args: Any, **kwargs: Any) -> Any:
            return self._monitor_execution(agent._original_call, scope, *args, **kwargs)

        def monitored_run(*args: Any, **kwargs: Any) -> Any:
            return self._monitor_execution(agent._original_run, scope, *args, **kwargs)

        def monitored_invoke(*args: Any, **kwargs: Any) -> Any:
            return self._monitor_execution(agent._original_invoke, scope, *args, **kwargs)

        if agent._original_call:
            agent.__call__ = monitored_call
        if agent._original_run:
            agent.run = monitored_run
        if agent._original_invoke:
            agent.invoke = monitored_invoke

        # Store scope reference
        agent._agentscope = scope

    def unwrap(self, agent: Any) -> None:
        """Remove monitoring from agent."""
        if hasattr(agent, "_original_call"):
            agent.__call__ = agent._original_call
        if hasattr(agent, "_original_run"):
            agent.run = agent._original_run
        if hasattr(agent, "_original_invoke"):
            agent.invoke = agent._original_invoke

        # Clean up
        if hasattr(agent, "_agentscope"):
            delattr(agent, "_agentscope")

    def supports(self, agent: Any) -> bool:
        """Check if agent is a LangChain agent."""
        agent_type = type(agent).__name__
        module = type(agent).__module__
        return "langchain" in module.lower() or agent_type.endswith("Agent")

    def _monitor_execution(
        self,
        original_method: Any,
        scope: "AgentScope",
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Monitor agent execution."""
        # Extract input
        input_text = self._extract_input(args, kwargs)
        scope._input = input_text

        scope.log_step(
            StepType.THOUGHT,
            f"Starting execution: {input_text[:100]}...",
            metadata={"input": input_text},
        )

        # Execute original method
        result = original_method(*args, **kwargs)

        # Extract output
        output_text = self._extract_output(result)
        scope._output = output_text

        scope.log_step(
            StepType.DECISION,
            f"Completed with result: {output_text[:100] if output_text else 'N/A'}...",
            metadata={"output": output_text},
        )

        return result

    def _extract_input(self, args: tuple, kwargs: dict) -> str:
        """Extract input from method arguments."""
        # Try common patterns
        if args:
            if isinstance(args[0], str):
                return args[0]
            elif isinstance(args[0], dict) and "input" in args[0]:
                return args[0]["input"]

        if "input" in kwargs:
            return kwargs["input"]
        elif "inputs" in kwargs:
            return str(kwargs["inputs"])

        return str(args) if args else str(kwargs)

    def _extract_output(self, result: Any) -> str:
        """Extract output from result."""
        if isinstance(result, str):
            return result
        elif isinstance(result, dict):
            # Common LangChain output keys
            for key in ["output", "result", "answer", "text"]:
                if key in result:
                    return str(result[key])
            return str(result)
        else:
            return str(result)
