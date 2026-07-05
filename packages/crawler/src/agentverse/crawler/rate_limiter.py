"""Rate limiting utilities for crawlers."""

import asyncio
import time


class RateLimiter:
    """Simple rate limiter with configurable requests per second."""

    def __init__(self, requests_per_second: float = 10.0) -> None:
        self._delay = 1.0 / requests_per_second
        self._last_call: float = 0.0

    async def acquire(self) -> None:
        """Wait if needed to respect the rate limit."""
        now = time.monotonic()
        wait = self._delay - (now - self._last_call)
        if wait > 0:
            await asyncio.sleep(wait)
        self._last_call = time.monotonic()