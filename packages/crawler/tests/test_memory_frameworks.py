"""Tests for memory framework crawler."""

import pytest

from agentverse.crawler.sources.memory_frameworks import (
    MemoryFrameworkCrawler,
    MEMORY_FRAMEWORKS,
    MEMORY_TYPES,
)


@pytest.mark.asyncio
async def test_crawler_returns_all_frameworks():
    """Crawler should return all defined memory frameworks."""
    crawler = MemoryFrameworkCrawler()
    result = await crawler.crawl()
    # Should have frameworks + memory types
    framework_items = [i for i in result.items if i.get("type") == "memory_framework"]
    type_items = [i for i in result.items if i.get("type") == "memory_type"]
    assert len(framework_items) == len(MEMORY_FRAMEWORKS)
    assert len(type_items) == len(MEMORY_TYPES)


@pytest.mark.asyncio
async def test_crawler_result_source():
    """Crawler result should have correct source."""
    crawler = MemoryFrameworkCrawler()
    result = await crawler.crawl()
    assert result.source == "memory_frameworks"


@pytest.mark.asyncio
async def test_crawler_framework_has_required_fields():
    """Each framework item should have required fields."""
    crawler = MemoryFrameworkCrawler()
    result = await crawler.crawl()
    for item in result.items:
        if item.get("type") == "memory_framework":
            assert "name" in item
            assert "description" in item
            assert "github_url" in item
            assert "memory_categories" in item


@pytest.mark.asyncio
async def test_crawler_memory_type_has_required_fields():
    """Each memory type item should have required fields."""
    crawler = MemoryFrameworkCrawler()
    result = await crawler.crawl()
    for item in result.items:
        if item.get("type") == "memory_type":
            assert "name" in item
            assert "description" in item
            assert "memory_category" in item


def test_memory_frameworks_list():
    """MEMORY_FRAMEWORKS should contain expected frameworks."""
    names = {f["name"] for f in MEMORY_FRAMEWORKS}
    assert "Mem0" in names
    assert "Zep" in names
    assert "LangMem" in names
    assert "Letta" in names
    assert "Cognee" in names


def test_memory_types_list():
    """MEMORY_TYPES should contain expected types."""
    names = {t["name"] for t in MEMORY_TYPES}
    assert "Short-term Memory" in names
    assert "Long-term Memory" in names
    assert "Episodic Memory" in names
    assert "Semantic Memory" in names
    assert "Graph Memory" in names
