"""Crawl pipeline orchestrator."""

from agentverse.crawler.base import CrawlResult


class CrawlPipeline:
    """Orchestrate multiple crawlers and aggregate results."""

    def __init__(self) -> None:
        self._crawlers: list = []

    def register(self, crawler) -> None:
        """Register a crawler for the pipeline."""
        self._crawlers.append(crawler)

    async def run_all(self, **kwargs) -> list[CrawlResult]:
        """Run all registered crawlers."""
        results: list[CrawlResult] = []
        for crawler in self._crawlers:
            result = await crawler.crawl(**kwargs)
            results.append(result)
        return results