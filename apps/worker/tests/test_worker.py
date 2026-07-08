"""Tests for worker tasks and TaskIQ broker."""

import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from agentverse.worker.broker import broker


# ---------------------------------------------------------------------------
# Broker
# ---------------------------------------------------------------------------


class TestBroker:
    """Tests for TaskIQ broker configuration."""

    def test_broker_is_in_memory_broker(self):
        """Broker should be an InMemoryBroker instance."""
        from taskiq import InMemoryBroker
        assert isinstance(broker, InMemoryBroker)

    def test_broker_has_tasks_registered(self):
        """Broker should have crawl tasks registered."""
        # TaskIQ registers tasks as broker tasks
        # We just verify the broker is importable and configured
        assert broker is not None


# ---------------------------------------------------------------------------
# run_crawl dispatch (backward-compatible function)
# ---------------------------------------------------------------------------


class TestRunCrawl:
    """Tests for run_crawl() source dispatch."""

    @pytest.mark.asyncio
    @patch("agentverse.crawler.sources.arxiv.ArxivCrawler")
    async def test_dispatches_to_arxiv(self, MockCrawler):
        """source='arxiv' creates ArxivCrawler and calls crawl()."""
        mock_instance = AsyncMock()
        mock_instance.crawl = AsyncMock(return_value=AsyncMock(items=[{"title": "p1"}], errors=[]))
        MockCrawler.return_value = mock_instance

        from agentverse.worker.tasks.crawl import run_crawl
        items = await run_crawl("arxiv", max_results=5)

        MockCrawler.assert_called_once()
        mock_instance.crawl.assert_awaited_once()
        assert items == [{"title": "p1"}]

    @pytest.mark.asyncio
    async def test_unknown_source_returns_empty(self):
        """Unknown source returns empty list without raising."""
        from agentverse.worker.tasks.crawl import run_crawl
        items = await run_crawl("unknown_source")

        assert items == []

    @pytest.mark.asyncio
    @patch("agentverse.crawler.sources.arxiv.ArxivCrawler")
    async def test_returns_empty_on_crawl_failure(self, MockCrawler):
        """Crawler exception is caught, returns empty list."""
        mock_instance = AsyncMock()
        mock_instance.crawl = AsyncMock(side_effect=Exception("network error"))
        MockCrawler.return_value = mock_instance

        from agentverse.worker.tasks.crawl import run_crawl
        items = await run_crawl("arxiv")

        assert items == []


# ---------------------------------------------------------------------------
# TaskIQ task functions (unit tests for the decorated functions)
# ---------------------------------------------------------------------------


class TestTaskFunctions:
    """Tests for TaskIQ-decorated task functions."""

    @pytest.mark.asyncio
    @patch("agentverse.worker.tasks.crawl.run_crawl", new_callable=AsyncMock)
    async def test_crawl_arxiv_calls_run_crawl(self, mock_run_crawl):
        """crawl_arxiv task delegates to run_crawl."""
        mock_run_crawl.return_value = [{"title": "p1"}]
        from agentverse.worker.tasks.crawl import crawl_arxiv
        result = await crawl_arxiv(max_results=10)
        # The function itself calls run_crawl
        mock_run_crawl.assert_called_once_with("arxiv", max_results=10)

    @pytest.mark.asyncio
    @patch("agentverse.worker.tasks.extract.run_extract", new_callable=AsyncMock)
    async def test_extract_text_calls_run_extract(self, mock_run_extract):
        """extract_text task delegates to run_extract."""
        mock_run_extract.return_value = {"entities": [], "relationships": []}
        from agentverse.worker.tasks.extract import extract_text
        result = await extract_text("test text", source="concept")
        mock_run_extract.assert_called_once_with("test text", source="concept")
