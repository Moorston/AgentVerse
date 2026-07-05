"""API-specific configuration."""

from agentverse.shared.config import Settings


class APISettings(Settings):
    """API-specific settings, inheriting from shared."""

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True