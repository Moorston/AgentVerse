"""Papers with Code API crawler — fetches papers with code implementations."""

from typing import Any

import httpx

from agentverse.crawler.base import BaseCrawler, CrawlResult
from agentverse.crawler.rate_limiter import RateLimiter
from agentverse.crawler.types import CrawlRequest
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

PWC_API_URL = "https://paperswithcode.com/api/v1"


class PapersWithCodeCrawler(BaseCrawler):
    """Crawl Papers with Code for papers with implementations."""

    def __init__(self, requests_per_second: float = 3.0) -> None:
        self._limiter = RateLimiter(requests_per_second=requests_per_second)

    async def crawl(
        self,
        request: CrawlRequest | None = None,
    ) -> CrawlResult:
        """Fetch papers from Papers with Code.

        Args:
            request: Structured request with optional ``query`` and ``max_results``
                fields.
        """
        r: CrawlRequest = request or {}
        query: str = r.get("query", "AI agent")
        max_results: int = r.get("max_results", 50)
        items: list[dict[str, Any]] = []
        errors: list[str] = []

        await self._limiter.acquire()
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    f"{PWC_API_URL}/papers/",
                    params={"q": query, "items_per_page": min(max_results, 50)},
                )
                response.raise_for_status()
                data = response.json()

                for paper in data.get("results", []):
                    items.append({
                        "paper_id": paper.get("id", ""),
                        "title": paper.get("title", ""),
                        "abstract": paper.get("abstract", ""),
                        "url_pdf": paper.get("url_pdf", ""),
                        "published": paper.get("published", ""),
                        "authors": paper.get("authors", []),
                        "proceeding": paper.get("proceeding", ""),
                    })
        except Exception as exc:
            errors.append(f"Error fetching Papers with Code: {exc}")

        logger.info("Papers with Code crawl complete", papers=len(items), errors=len(errors))
        return CrawlResult(source="papers_with_code", items=items, errors=errors)