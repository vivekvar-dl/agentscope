"""
AgentScope - The Missing Debugger for AI Agents

Track, debug, and optimize your AI agents with real-time monitoring,
cost analytics, and execution replay.
"""

from agentscope.core.scope import AgentScope
from agentscope.core.metrics import Metrics, ExecutionTrace
from agentscope.core.exceptions import AgentScopeError, AdapterError

__version__ = "0.1.0"
__author__ = "Vivek"
__license__ = "MIT"

__all__ = [
    "AgentScope",
    "Metrics",
    "ExecutionTrace",
    "AgentScopeError",
    "AdapterError",
]
