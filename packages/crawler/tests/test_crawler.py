"""Tests for crawler base and rate limiter."""

import asyncio
import pytest

from agentverse.crawler.base import CrawlResult, BaseCrawler
from agentverse.crawler.rate_limiter import RateLimiter


def test_crawl_result_defaults():
    """Test CrawlResult default values."""
    result = CrawlResult(source="test")
    assert result.source == "test"
    assert result.items == []
    assert result.errors == []


def test_crawl_result_with_items():
    """Test CrawlResult with items."""
    result = CrawlResult(source="test", items=[{"title": "paper1"}, {"title": "paper2"}])
    assert len(result.items) == 2


def test_crawl_result_with_errors():
    """Test CrawlResult with errors."""
    result = CrawlResult(source="test", errors=["error1", "error2"])
    assert len(result.errors) == 2


@pytest.mark.asyncio
async def test_rate_limiter():
    """Test RateLimiter acquires correctly."""
    limiter = RateLimiter(requests_per_second=100)  # Very fast for testing
    start = asyncio.get_event_loop().time()
    await limiter.acquire()
    await limiter.acquire()
    elapsed = asyncio.get_event_loop().time() - start
    # Should be very fast with 100 req/s
    assert elapsed < 0.1