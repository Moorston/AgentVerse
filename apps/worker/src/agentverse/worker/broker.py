"""TaskIQ broker configuration for AgentVerse worker.

Uses MemoryBroker for zero-dependency in-process execution.
To switch to distributed execution, replace with RedisBroker:

    from taskiq_redis import RedisBroker
    broker = RedisBroker("redis://localhost:6379")
"""

import asyncio

from taskiq import InMemoryBroker, TaskiqEvents, TaskiqState

from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

broker = InMemoryBroker()


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
