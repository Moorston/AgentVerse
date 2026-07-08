"""Crawl tasks — dispatches to appropriate crawler sources."""

import asyncio
from typing import Any

from agentverse.crawler.types import CrawlRequest
from agentverse.shared.logging import get_logger
from agentverse.worker.broker import broker

logger = get_logger(__name__)


async def run_crawl(source: str = "arxiv", **kwargs: Any) -> list[dict]:
    """Execute a crawl task and return crawled items.

    Args:
        source: Data source identifier (arxiv, github, rss, semantic_scholar).

    Returns:
        List of crawled items as dicts.
    """
    logger.info("Starting crawl", source=source)

    try:
        if source == "arxiv":
            from agentverse.crawler.sources.arxiv import ArxivCrawler
            crawler = ArxivCrawler()
        elif source == "github":
            from agentverse.crawler.sources.github import GitHubCrawler
            crawler = GitHubCrawler()
        elif source == "rss":
            from agentverse.crawler.sources.rss import RSSCrawler
            crawler = RSSCrawler()
        elif source == "semantic_scholar":
            from agentverse.crawler.sources.semantic_scholar import SemanticScholarCrawler
            crawler = SemanticScholarCrawler()
        else:
            logger.warning("Unknown crawl source", source=source)
            return []

        request: CrawlRequest = kwargs  # type: ignore[assignment]
        result = await crawler.crawl(request)

        if result.errors:
            logger.warning("Crawl errors", source=source, errors=result.errors)

        logger.info("Crawl complete", source=source, items=len(result.items))
        return result.items

    except Exception as exc:
        logger.error("Crawl failed", source=source, error=str(exc))
        return []


# ---------------------------------------------------------------------------
# TaskIQ task definitions — declarative retry and chaining
# ---------------------------------------------------------------------------


@broker.task(
    task_name="crawl_arxiv",
    retry_on_error=True,
    max_retries=3,
)
async def crawl_arxiv(max_results: int = 100) -> list[dict]:
    """Crawl arXiv for AI Agent papers."""
    logger.info("=== TaskIQ: crawl_arxiv starting ===")
    items = await run_crawl("arxiv", max_results=max_results)
    logger.info("=== TaskIQ: crawl_arxiv complete ===", items=len(items))
    return items


@broker.task(
    task_name="crawl_github",
    retry_on_error=True,
    max_retries=3,
)
async def crawl_github() -> list[dict]:
    """Crawl GitHub for AI Agent frameworks."""
    logger.info("=== TaskIQ: crawl_github starting ===")
    items = await run_crawl("github")
    logger.info("=== TaskIQ: crawl_github complete ===", items=len(items))
    return items


@broker.task(
    task_name="crawl_rss",
    retry_on_error=True,
    max_retries=3,
)
async def crawl_rss() -> list[dict]:
    """Crawl RSS feeds for AI Agent news."""
    logger.info("=== TaskIQ: crawl_rss starting ===")
    items = await run_crawl("rss")
    logger.info("=== TaskIQ: crawl_rss complete ===", items=len(items))
    return items
