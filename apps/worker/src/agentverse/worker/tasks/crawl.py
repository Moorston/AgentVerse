"""Crawl task — dispatches to appropriate crawler."""

from typing import Any

from agentverse.crawler.types import CrawlRequest
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


async def run_crawl(source: str = "arxiv", **kwargs: Any) -> list[dict]:
    """Execute a crawl task and return crawled items.

    Args:
        source: Data source identifier (arxiv, github, semantic_scholar, rss).

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