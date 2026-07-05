"""In-memory rate limiter middleware for FastAPI."""

import time
from collections import defaultdict

from fastapi import Request
from fastapi.responses import JSONResponse

from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """In-memory sliding window rate limiter."""

    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000) -> None:
        self._rpm = requests_per_minute
        self._rph = requests_per_hour
        self._minute_windows: dict[str, list[float]] = defaultdict(list)
        self._hour_windows: dict[str, list[float]] = defaultdict(list)

    def _get_client_id(self, request: Request) -> str:
        """Extract client identifier from request."""
        forwarded = request.headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _clean_window(self, window: list[float], duration: float) -> list[float]:
        """Remove expired entries from sliding window."""
        cutoff = time.monotonic() - duration
        return [t for t in window if t > cutoff]

    def is_allowed(self, request: Request) -> tuple[bool, dict[str, str]]:
        """Check if request is within rate limits.

        Returns:
            (is_allowed, headers) tuple.
        """
        client_id = self._get_client_id(request)
        now = time.monotonic()

        # Clean windows
        self._minute_windows[client_id] = self._clean_window(
            self._minute_windows[client_id], 60.0
        )
        self._hour_windows[client_id] = self._clean_window(
            self._hour_windows[client_id], 3600.0
        )

        # Record this request BEFORE computing headers
        # so that remaining reflects the current request
        self._minute_windows[client_id].append(now)
        self._hour_windows[client_id].append(now)

        minute_count = len(self._minute_windows[client_id])
        hour_count = len(self._hour_windows[client_id])

        headers = {
            "X-RateLimit-Limit-Minute": str(self._rpm),
            "X-RateLimit-Remaining-Minute": str(max(0, self._rpm - minute_count)),
            "X-RateLimit-Limit-Hour": str(self._rph),
            "X-RateLimit-Remaining-Hour": str(max(0, self._rph - hour_count)),
        }

        if minute_count > self._rpm:
            retry_after = int(60 - (now - self._minute_windows[client_id][0]))
            headers["Retry-After"] = str(max(1, retry_after))
            return False, headers

        if hour_count > self._rph:
            retry_after = int(3600 - (now - self._hour_windows[client_id][0]))
            headers["Retry-After"] = str(max(1, retry_after))
            return False, headers

        return True, headers


# Global rate limiter instance
_rate_limiter = RateLimiter(requests_per_minute=60, requests_per_hour=1000)


def get_rate_limiter() -> RateLimiter:
    """Return the global rate limiter."""
    return _rate_limiter