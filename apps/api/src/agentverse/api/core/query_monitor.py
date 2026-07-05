"""Database query performance monitoring."""

import time
from typing import Any
from functools import wraps

from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

# Slow query threshold in milliseconds
SLOW_QUERY_THRESHOLD_MS = 100

# Query statistics
_query_stats: dict[str, dict[str, Any]] = {}


def monitor_query(query_name: str):
    """Decorator to monitor query performance.

    Usage:
        @monitor_query("list_concepts")
        async def list_concepts(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.monotonic()
            try:
                result = await func(*args, **kwargs)
                elapsed_ms = (time.monotonic() - start) * 1000

                # Update stats
                if query_name not in _query_stats:
                    _query_stats[query_name] = {
                        "count": 0,
                        "total_ms": 0,
                        "max_ms": 0,
                        "slow_count": 0,
                    }
                stats = _query_stats[query_name]
                stats["count"] += 1
                stats["total_ms"] += elapsed_ms
                stats["max_ms"] = max(stats["max_ms"], elapsed_ms)

                if elapsed_ms > SLOW_QUERY_THRESHOLD_MS:
                    stats["slow_count"] += 1
                    logger.warning(
                        "Slow query detected",
                        query=query_name,
                        elapsed_ms=round(elapsed_ms, 2),
                        threshold_ms=SLOW_QUERY_THRESHOLD_MS,
                    )

                return result
            except Exception as exc:
                elapsed_ms = (time.monotonic() - start) * 1000
                logger.error(
                    "Query failed",
                    query=query_name,
                    elapsed_ms=round(elapsed_ms, 2),
                    error=str(exc),
                )
                raise
        return wrapper
    return decorator


def get_query_stats() -> dict[str, dict[str, Any]]:
    """Return query performance statistics."""
    result = {}
    for name, stats in _query_stats.items():
        avg_ms = stats["total_ms"] / stats["count"] if stats["count"] > 0 else 0
        result[name] = {
            "count": stats["count"],
            "avg_ms": round(avg_ms, 2),
            "max_ms": round(stats["max_ms"], 2),
            "slow_count": stats["slow_count"],
            "slow_pct": round(stats["slow_count"] / stats["count"] * 100, 1) if stats["count"] > 0 else 0,
        }
    return result


def reset_query_stats() -> None:
    """Reset all query statistics."""
    _query_stats.clear()