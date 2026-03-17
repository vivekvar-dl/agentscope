"""Custom exceptions for AgentScope."""


class AgentScopeError(Exception):
    """Base exception for all AgentScope errors."""

    pass


class AdapterError(AgentScopeError):
    """Raised when an adapter fails to wrap an agent."""

    pass


class ExportError(AgentScopeError):
    """Raised when export operation fails."""

    pass


class ReplayError(AgentScopeError):
    """Raised when replay operation fails."""

    pass


class ConfigurationError(AgentScopeError):
    """Raised when configuration is invalid."""

    pass
