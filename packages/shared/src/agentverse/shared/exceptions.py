"""Base exception hierarchy for AgentVerse."""


class AgentVerseError(Exception):
    """Base exception for all AgentVerse errors."""


class ConfigurationError(AgentVerseError):
    """Raised when a configuration value is missing or invalid."""


class DatabaseError(AgentVerseError):
    """Raised on database connection or query failures."""


class NotFoundError(AgentVerseError):
    """Raised when a requested resource is not found."""