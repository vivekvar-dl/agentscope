"""Base adapter interface for agent frameworks."""

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from agentscope.core.scope import AgentScope


class BaseAdapter(ABC):
    """Base class for agent framework adapters."""

    @abstractmethod
    def wrap(self, agent: Any, scope: "AgentScope") -> None:
        """
        Wrap an agent to enable monitoring.
        
        Args:
            agent: The agent instance to wrap
            scope: The AgentScope instance
        """
        pass

    @abstractmethod
    def unwrap(self, agent: Any) -> None:
        """
        Remove monitoring from an agent.
        
        Args:
            agent: The wrapped agent instance
        """
        pass

    @abstractmethod
    def supports(self, agent: Any) -> bool:
        """
        Check if this adapter supports the given agent.
        
        Args:
            agent: Agent instance to check
        
        Returns:
            True if supported, False otherwise
        """
        pass
