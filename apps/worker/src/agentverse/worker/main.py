"""Worker entry point — TaskIQ-based knowledge pipeline orchestration.

Two modes of operation:

1. **Worker mode** (default): Starts the TaskIQ worker that executes tasks.
   Run: ``python -m agentverse.worker.main``

2. **Scheduler mode**: Starts the interval-based scheduler that enqueues tasks.
   Run: ``python -m agentverse.worker.main --scheduler``

For production, run both in separate processes:
   Terminal 1: ``taskiq worker agentverse.worker.broker:broker``
   Terminal 2: ``python -m agentverse.worker.main --scheduler``
"""

import asyncio
import sys
import traceback

from agentverse.shared.logging import get_logger
from agentverse.worker.config import WorkerSettings

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Scheduler — interval-based task enqueuing
# ---------------------------------------------------------------------------


async def run_scheduler() -> None:
    """Run the task scheduler that enqueues tasks at configured intervals."""
    from agentverse.worker.broker import broker
    from agentverse.worker.tasks.crawl import crawl_arxiv, crawl_github, crawl_rss

    settings = WorkerSettings()
    logger.info("scheduler_starting", environment=settings.environment)

    # Task definitions: (name, task_func, interval_seconds)
    scheduled_tasks: list[tuple[str, any, int]] = [
        ("crawl_arxiv", crawl_arxiv, 86400),       # Daily
        ("crawl_github", crawl_github, 604800),    # Weekly
        ("crawl_rss", crawl_rss, 86400),           # Daily
    ]

    async def task_loop(name: str, task_func, interval: int) -> None:
        """Run a task on a fixed interval, logging all lifecycle events."""
        while True:
            try:
                logger.info("task_enqueueing", name=name)
                await task_func.kiq()  # Enqueue to TaskIQ broker
                logger.info("task_enqueued", name=name)
            except Exception as exc:
                logger.error(
                    "task_enqueue_failed",
                    name=name,
                    error=str(exc),
                    traceback=traceback.format_exc()[:500],
                )
            await asyncio.sleep(interval)

    logger.info("scheduler_configured", tasks=len(scheduled_tasks))

    await asyncio.gather(*[
        task_loop(name, func, interval)
        for name, func, interval in scheduled_tasks
    ])


# ---------------------------------------------------------------------------
# Worker — TaskIQ task execution
# ---------------------------------------------------------------------------


async def run_worker() -> None:
    """Run the TaskIQ worker in-process (for development/testing).

    For production, use the CLI: ``taskiq worker agentverse.worker.broker:broker``
    """
    from agentverse.worker.broker import broker
    # Import tasks to register them with the broker
    import agentverse.worker.tasks.crawl  # noqa: F401
    import agentverse.worker.tasks.extract  # noqa: F401
    import agentverse.worker.tasks.index  # noqa: F401

    settings = WorkerSettings()
    logger.info("worker_starting_inprocess", environment=settings.environment)

    # TaskIQ's async worker loop
    await broker.startup()
    try:
        while True:
            # Poll for tasks and execute them
            await broker.listen()
    except KeyboardInterrupt:
        logger.info("worker_interrupted")
    finally:
        await broker.shutdown()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


async def main() -> None:
    """Main entry point — dispatches to worker or scheduler mode."""
    if "--scheduler" in sys.argv:
        await run_scheduler()
    else:
        await run_worker()


if __name__ == "__main__":
    asyncio.run(main())
