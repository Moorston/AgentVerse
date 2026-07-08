"""Tests for API rate limiter."""

import time
from agentverse.api.core.rate_limiter import RateLimiter


class MockRequest:
    """Mock FastAPI Request for testing."""
    def __init__(self, host: str = "127.0.0.1") -> None:
        self.headers = {}
        self.client = type("Client", (), {"host": host})()


def test_rate_limiter_allows_within_limit():
    """Test that requests within limit are allowed."""
    limiter = RateLimiter(requests_per_minute=10, requests_per_hour=100)
    request = MockRequest()
    allowed, headers = limiter.is_allowed(request)
    assert allowed is True
    assert "X-RateLimit-Limit-Minute" in headers


def test_rate_limiter_blocks_when_exceeded():
    """Test that excess requests are blocked."""
    limiter = RateLimiter(requests_per_minute=2, requests_per_hour=100)
    request = MockRequest()
    limiter.is_allowed(request)
    limiter.is_allowed(request)
    allowed, headers = limiter.is_allowed(request)
    assert allowed is False
    assert "Retry-After" in headers


def test_rate_limiter_per_client():
    """Test that rate limits are per-client."""
    limiter = RateLimiter(requests_per_minute=1, requests_per_hour=100)
    req1 = MockRequest(host="10.0.0.1")
    req2 = MockRequest(host="10.0.0.2")
    allowed1, _ = limiter.is_allowed(req1)
    allowed2, _ = limiter.is_allowed(req2)
    assert allowed1 is True
    assert allowed2 is True


def test_rate_limiter_headers():
    """Test that rate limit headers are correct (remaining counted before recording)."""
    limiter = RateLimiter(requests_per_minute=100, requests_per_hour=1000)
    request = MockRequest()
    _, headers = limiter.is_allowed(request)
    assert headers["X-RateLimit-Limit-Minute"] == "100"
    assert headers["X-RateLimit-Remaining-Minute"] == "100"
    assert headers["X-RateLimit-Limit-Hour"] == "1000"
    assert headers["X-RateLimit-Remaining-Hour"] == "1000"