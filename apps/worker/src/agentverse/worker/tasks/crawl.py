"""Crawl task — dispatches to appropriate crawler."""

from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


async def run_crawl(source: str = "arxiv", **kwargs) -> list[dict]:
    """Execute a crawl task and return crawled items.

    Args:
        source: Data source identifier (arxiv, github, semantic_scholar, rss).

    Returns:
        List of crawled items as dicts.
    """
    logger.info("Starting crawl", source=source)

    if source == "arxiv":
        from agentverse.crawler.sources.arxiv import ArxivCrawler
        crawler = ArxivCrawler()
        result = await crawler.crawl(**kwargs)
    elif source == "github":
        from agentverse.crawler.sources.github import GitHubCrawler
        crawler = GitHubCrawler()
        result = await crawler.crawl(**kwargs)
    else:
        logger.warning("Unknown crawl source", source=source)
        return []

    if result.errors:
        logger.warning("Crawl errors", source=source, errors=result.errors)

    logger.info("Crawl complete", source=source, items=len(result.items))
    return result.items