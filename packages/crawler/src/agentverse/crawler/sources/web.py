"""General web crawler — fetches and parses web pages for Agent content."""

from typing import Any

import httpx
from bs4 import BeautifulSoup

from agentverse.crawler.base import BaseCrawler, CrawlResult
from agentverse.crawler.rate_limiter import RateLimiter
from agentverse.crawler.types import CrawlRequest
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


class WebCrawler(BaseCrawler):
    """Crawl general web pages for Agent content.

    Extracts title, description, links, and metadata from web pages.
    Respects rate limiting to avoid overwhelming target servers.
    """

    def __init__(self, requests_per_second: float = 2.0) -> None:
        self._limiter = RateLimiter(requests_per_second=requests_per_second)

    async def crawl(
        self,
        request: CrawlRequest | None = None,
    ) -> CrawlResult:
        """Fetch and parse a web page.

        Args:
            request: Structured request. Uses ``query`` as the URL to crawl.
                Accepts ``url`` as an alias for ``query``.
        """
        r: CrawlRequest = request or {}
        url: str = r.get("url", "") or r.get("query", "")
        if not url:
            return CrawlResult(source="web", items=[], errors=["No URL provided"])

        await self._limiter.acquire()

        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                title = soup.title.string.strip() if soup.title and soup.title.string else url

                # Extract meta description
                meta_desc = ""
                meta_tag = soup.find("meta", attrs={"name": "description"})
                if meta_tag and meta_tag.get("content"):
                    meta_desc = meta_tag["content"].strip()

                # Extract main text content (strip scripts/styles)
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                text = soup.get_text(separator="\n", strip=True)

                # Extract links
                links = []
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if href.startswith("http"):
                        links.append({"text": a.get_text(strip=True), "url": href})

                item = {
                    "url": url,
                    "title": title,
                    "description": meta_desc,
                    "text": text[:5000],  # Truncate long pages
                    "links": links[:100],
                    "status_code": response.status_code,
                }

                logger.info("Web crawl complete", url=url, title=title[:50], links=len(links))
                return CrawlResult(source="web", items=[item], errors=[])

        except httpx.HTTPStatusError as exc:
            error = f"HTTP {exc.response.status_code} for {url}"
            logger.warning("Web crawl HTTP error", url=url, error=error)
            return CrawlResult(source="web", items=[], errors=[error])

        except Exception as exc:
            error = f"Error crawling {url}: {exc}"
            logger.warning("Web crawl failed", url=url, error=str(exc))
            return CrawlResult(source="web", items=[], errors=[error])
