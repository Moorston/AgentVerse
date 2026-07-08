"""TaskIQ broker configuration for AgentVerse worker.

Supports two backends:
- **InMemoryBroker** (default): Zero-dependency in-process execution for development.
- **RedisBroker**: Distributed execution for production.

Controlled by the ``TASKIQ_BROKER`` environment variable:
  - ``inmemory`` (default) → InMemoryBroker
  - ``redis`` → RedisBroker(settings.taskiq_redis_dsn)
"""

import asyncio

from taskiq import InMemoryBroker, TaskiqEvents, TaskiqState

from agentverse.shared.logging import get_logger
from agentverse.worker.config import WorkerSettings

logger = get_logger(__name__)

# Resolve broker type from environment
_settings = WorkerSettings()

if _settings.taskiq_broker == "redis":
    try:
        from taskiq_redis import RedisBroker
        broker = RedisBroker(_settings.taskiq_redis_dsn)
        logger.info("Broker: RedisBroker", dsn=_settings.taskiq_redis_dsn)
    except ImportError:
        logger.warning("RedisBroker not available (install taskiq_redis), falling back to InMemoryBroker")
        broker = InMemoryBroker()
else:
    broker = InMemoryBroker()
    logger.info("Broker: InMemoryBroker")


# ---------------------------------------------------------------------------
# Event hooks — retry backoff and lifecycle logging
# ---------------------------------------------------------------------------


@broker.task
async def _noop() -> None:
    """Placeholder to ensure broker is importable."""


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    """Log worker startup."""
    logger.info("taskiq_worker_startup")


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(state: TaskiqState) -> None:
    """Log worker shutdown."""
    logger.info("taskiq_worker_shutdown")


async def retry_backoff(retries: int) -> None:
    """Exponential backoff delay for retries: 1s, 2s, 4s."""
    delay = 2 ** retries
    logger.info("retry_backoff", retries=retries, delay_seconds=delay)
    await asyncio.sleep(delay)