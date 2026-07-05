"""Retry with exponential backoff."""

import asyncio
import functools
import logging

logger = logging.getLogger(__name__)


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator: retry an async function with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    if attempt < max_attempts:
                        wait = delay * (backoff ** (attempt - 1))
                        logger.warning(
                            "Retry %d/%d after error: %s. Waiting %.1fs...",
                            attempt, max_attempts, exc, wait,
                        )
                        await asyncio.sleep(wait)
            raise last_exc  # type: ignore
        return wrapper
    return decorator