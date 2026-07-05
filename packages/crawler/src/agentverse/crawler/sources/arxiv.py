"""ArXiv paper crawler — fetches recent AI/ML papers via arXiv API."""

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

import httpx

from agentverse.crawler.base import BaseCrawler, CrawlResult
from agentverse.crawler.rate_limiter import RateLimiter
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

ARXIV_API_URL = "http://export.arxiv.org/api/query"
ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom"}

# AI/ML relevant categories
DEFAULT_CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.MA", "cs.CV"]


class ArxivCrawler(BaseCrawler):
    """Crawl ArXiv for AI Agent papers."""

    def __init__(self, requests_per_second: float = 3.0) -> None:
        self._limiter = RateLimiter(requests_per_second=requests_per_second)

    async def crawl(
        self,
        categories: list[str] | None = None,
        max_results: int = 100,
        since: str = "",
        search_query: str = "",
        **kwargs: Any,
    ) -> CrawlResult:
        """Fetch recent papers from ArXiv API.

        Args:
            categories: ArXiv categories to search (default: cs.AI, cs.LG, cs.CL).
            max_results: Maximum number of papers to return.
            since: ISO date string to filter papers published after this date.
            search_query: Additional search query terms.
        """
        cats = categories or DEFAULT_CATEGORIES
        cat_query = " OR ".join(f"cat:{cat}" for cat in cats)
        query = f"({cat_query})"
        if search_query:
            query += f" AND all:{search_query}"

        items: list[dict[str, Any]] = []
        errors: list[str] = []
        start = 0

        while len(items) < max_results:
            batch_size = min(100, max_results - len(items))
            params = {
                "search_query": query,
                "start": start,
                "max_results": batch_size,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            }

            await self._limiter.acquire()
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(ARXIV_API_URL, params=params)
                    response.raise_for_status()
                    papers = self._parse_response(response.text, since=since)
                    if not papers:
                        break
                    items.extend(papers)
                    start += batch_size
            except httpx.HTTPStatusError as exc:
                errors.append(f"HTTP {exc.response.status_code}: {exc.response.text[:200]}")
                break
            except Exception as exc:
                errors.append(f"Error fetching arXiv: {exc}")
                break

        logger.info("ArXiv crawl complete", papers=len(items), errors=len(errors))
        return CrawlResult(source="arxiv", items=items, errors=errors)

    def _parse_response(self, xml_text: str, since: str = "") -> list[dict[str, Any]]:
        """Parse arXiv Atom XML response into structured paper dicts."""
        root = ET.fromstring(xml_text)
        papers: list[dict[str, Any]] = []

        for entry in root.findall("atom:entry", ARXIV_NS):
            paper = self._parse_entry(entry)
            if since and paper.get("published_date", "") < since:
                continue
            papers.append(paper)

        return papers

    def _parse_entry(self, entry: ET.Element) -> dict[str, Any]:
        """Parse a single arXiv Atom entry."""
        title = self._text(entry, "atom:title", "").strip().replace("\n", " ")
        abstract = self._text(entry, "atom:summary", "").strip().replace("\n", " ")
        published = self._text(entry, "atom:published", "")
        updated = self._text(entry, "atom:updated", "")

        authors = []
        for author_elem in entry.findall("atom:author", ARXIV_NS):
            name = self._text(author_elem, "atom:name", "")
            if name:
                authors.append(name)

        categories = []
        for cat_elem in entry.findall("atom:category", ARXIV_NS):
            term = cat_elem.get("term", "")
            if term:
                categories.append(term)

        doi = ""
        doi_elem = entry.find("atom:doi", ARXIV_NS)
        if doi_elem is not None and doi_elem.text:
            doi = doi_elem.text

        arxiv_id = ""
        id_elem = entry.find("atom:id", ARXIV_NS)
        if id_elem is not None and id_elem.text:
            arxiv_id = id_elem.text.split("/abs/")[-1]

        # Parse published date to ISO format
        published_date = ""
        if published:
            try:
                dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                published_date = dt.strftime("%Y-%m-%d")
            except ValueError:
                published_date = published[:10]

        return {
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "doi": doi,
            "arxiv_id": arxiv_id,
            "categories": categories,
            "published_date": published_date,
            "updated": updated[:10] if updated else "",
        }

    def _text(self, elem: ET.Element, path: str, default: str = "") -> str:
        """Extract text from an XML element."""
        child = elem.find(path, ARXIV_NS)
        return child.text if child is not None and child.text else default