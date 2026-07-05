"""Semantic Scholar API crawler — fetches paper metadata and citation data."""

from typing import Any

import httpx

from agentverse.crawler.base import BaseCrawler, CrawlResult
from agentverse.crawler.rate_limiter import RateLimiter
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

S2_API_URL = "https://api.semanticscholar.org/graph/v1"


class SemanticScholarCrawler(BaseCrawler):
    """Crawl Semantic Scholar for paper metadata and citations."""

    def __init__(self, api_key: str = "", requests_per_second: float = 5.0) -> None:
        self._api_key = api_key
        self._limiter = RateLimiter(requests_per_second=requests_per_second)

    async def crawl(
        self,
        query: str = "",
        arxiv_ids: list[str] | None = None,
        max_results: int = 50,
        **kwargs: Any,
    ) -> CrawlResult:
        """Fetch paper data from Semantic Scholar.

        Args:
            query: Search query.
            arxiv_ids: List of arXiv IDs to look up.
            max_results: Maximum results.
        """
        items: list[dict[str, Any]] = []
        errors: list[str] = []

        headers = {}
        if self._api_key:
            headers["x-api-key"] = self._api_key

        # Look up by arXiv IDs
        if arxiv_ids:
            for arxiv_id in arxiv_ids[:max_results]:
                await self._limiter.acquire()
                try:
                    paper = await self._fetch_paper_by_arxiv(arxiv_id, headers)
                    if paper:
                        items.append(paper)
                except Exception as exc:
                    errors.append(f"Error fetching arXiv {arxiv_id}: {exc}")

        # Search by query
        if query and len(items) < max_results:
            await self._limiter.acquire()
            try:
                search_items = await self._search_papers(query, max_results - len(items), headers)
                items.extend(search_items)
            except Exception as exc:
                errors.append(f"Error searching: {exc}")

        logger.info("Semantic Scholar crawl complete", papers=len(items), errors=len(errors))
        return CrawlResult(source="semantic_scholar", items=items, errors=errors)

    async def _fetch_paper_by_arxiv(self, arxiv_id: str, headers: dict[str, str]) -> dict[str, Any] | None:
        """Fetch paper by arXiv ID."""
        fields = "paperId,title,abstract,authors,citationCount,influentialCitationCount,year,externalIds,references"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{S2_API_URL}/paper/ARXIV:{arxiv_id}",
                params={"fields": fields},
                headers=headers,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()

            authors = [a.get("name", "") for a in data.get("authors", [])]
            references = [r.get("paperId", "") for r in data.get("references", [])[:20]]

            return {
                "paper_id": data.get("paperId", ""),
                "title": data.get("title", ""),
                "abstract": data.get("abstract", ""),
                "authors": authors,
                "year": data.get("year"),
                "citation_count": data.get("citationCount", 0),
                "influential_citation_count": data.get("influentialCitationCount", 0),
                "arxiv_id": arxiv_id,
                "reference_count": len(references),
            }

    async def _search_papers(self, query: str, limit: int, headers: dict[str, str]) -> list[dict[str, Any]]:
        """Search papers by query."""
        fields = "paperId,title,abstract,authors,citationCount,year"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{S2_API_URL}/paper/search",
                params={"query": query, "limit": limit, "fields": fields},
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

            items = []
            for paper in data.get("data", []):
                authors = [a.get("name", "") for a in paper.get("authors", [])]
                items.append({
                    "paper_id": paper.get("paperId", ""),
                    "title": paper.get("title", ""),
                    "abstract": paper.get("abstract", ""),
                    "authors": authors,
                    "year": paper.get("year"),
                    "citation_count": paper.get("citationCount", 0),
                })
            return items