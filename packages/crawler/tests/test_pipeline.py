"""Tests for crawler pipeline."""

import pytest

from agentverse.crawler.base import BaseCrawler, CrawlResult
from agentverse.crawler.pipeline import CrawlPipeline


class MockCrawler(BaseCrawler):
    """Mock crawler for testing."""

    def __init__(self, items: list[dict] | None = None):
        self._items = items or [{"title": "test"}]

    async def crawl(self, **kwargs) -> CrawlResult:
        return CrawlResult(source="mock", items=self._items)


@pytest.mark.asyncio
async def test_pipeline_empty():
    """Empty pipeline should return empty results."""
    pipeline = CrawlPipeline()
    results = await pipeline.run_all()
    assert results == []


@pytest.mark.asyncio
async def test_pipeline_single_crawler():
    """Pipeline should run registered crawler."""
    pipeline = CrawlPipeline()
    pipeline.register(MockCrawler([{"title": "paper1"}]))
    results = await pipeline.run_all()
    assert len(results) == 1
    assert results[0].items == [{"title": "paper1"}]


@pytest.mark.asyncio
async def test_pipeline_multiple_crawlers():
    """Pipeline should run all registered crawlers."""
    pipeline = CrawlPipeline()
    pipeline.register(MockCrawler([{"title": "a"}]))
    pipeline.register(MockCrawler([{"title": "b"}]))
    results = await pipeline.run_all()
    assert len(results) == 2
