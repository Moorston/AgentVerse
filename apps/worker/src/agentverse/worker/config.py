"""Worker-specific configuration."""

from agentverse.shared.config import Settings


class WorkerSettings(Settings):
    """Worker settings, inheriting from shared."""
    poll_interval: int = 60
    max_concurrent_tasks: int = 5
    taskiq_broker: str = "inmemory"
    taskiq_redis_dsn: str = "redis://localhost:6379/0"