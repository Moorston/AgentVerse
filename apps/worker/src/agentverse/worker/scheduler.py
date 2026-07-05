"""Task scheduler / cron — interval-based task orchestration."""

import asyncio
import traceback
from typing import Any, Callable, Awaitable

from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


class Scheduler:
    """Simple interval-based task scheduler.

    Tasks run on their configured intervals. Failed tasks are logged
    but do not stop the scheduler.
    """

    def __init__(self) -> None:
        self._tasks: list[tuple[str, Callable[[], Awaitable[None]], int]] = []

    def register(self, name: str, task: Callable[[], Awaitable[None]], interval_seconds: int) -> None:
        """Register a recurring task.

        Args:
            name: Task name for logging.
            task: Async callable to execute.
            interval_seconds: Seconds between executions.
        """
        self._tasks.append((name, task, interval_seconds))
        logger.info("Task registered", name=name, interval=interval_seconds)

    async def run(self) -> None:
        """Run all registered tasks on their intervals."""
        logger.info("Scheduler starting", task_count=len(self._tasks))

        async def _loop(name: str, task: Callable[[], Awaitable[None]], interval: int) -> None:
            """Run a task in a loop with the given interval."""
            while True:
                try:
                    logger.info("Task starting", name=name)
                    start_time = asyncio.get_event_loop().time()
                    await task()
                    elapsed = asyncio.get_event_loop().time() - start_time
                    logger.info("Task complete", name=name, elapsed_seconds=round(elapsed, 2))
                except Exception as exc:
                    logger.error(
                        "Task failed",
                        name=name,
                        error=str(exc),
                        traceback=traceback.format_exc()[:500],
                    )
                await asyncio.sleep(interval)

        await asyncio.gather(*[
            _loop(name, task, interval)
            for name, task, interval in self._tasks
        ])