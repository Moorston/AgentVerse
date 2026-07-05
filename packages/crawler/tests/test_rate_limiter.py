"""Tests for crawler rate limiter."""

import asyncio
import time

import pytest

from agentverse.crawler.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_allows_within_limit():
    """Should allow requests within the rate limit."""
    limiter = RateLimiter(requests_per_second=100)
    # Should not block
    await limiter.acquire()
    await limiter.acquire()


@pytest.mark.asyncio
async def test_rate_limiter_delays_when_exceeded():
    """Should delay when rate limit is exceeded."""
    limiter = RateLimiter(requests_per_second=10)
    start = time.monotonic()
    for _ in range(15):
        await limiter.acquire()
    elapsed = time.monotonic() - start
    # Should have taken some time due to rate limiting
    assert elapsed > 0.1  # At least some delay


def test_rate_limiter_default():
    """Default rate limiter should initialize."""
    limiter = RateLimiter()
    assert limiter._delay > 0
