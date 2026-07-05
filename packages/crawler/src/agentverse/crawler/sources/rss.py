"""RSS feed crawler — fetches news from AI industry RSS feeds."""

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

import httpx

from agentverse.crawler.base import BaseCrawler, CrawlResult
from agentverse.crawler.rate_limiter import RateLimiter
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

# Default RSS feeds for AI industry news
DEFAULT_FEEDS: dict[str, str] = {
    "huggingface_papers": "https://huggingface.co/papers/rss",
    "openai_blog": "https://openai.com/blog/rss.xml",
    "anthropic_blog": "https://www.anthropic.com/feed.xml",
}


class RSSCrawler(BaseCrawler):
    """Crawl RSS feeds for AI industry news and papers."""

    def __init__(self, requests_per_second: float = 2.0) -> None:
        self._limiter = RateLimiter(requests_per_second=requests_per_second)

    async def crawl(
        self,
        feeds: dict[str, str] | None = None,
        since: str = "",
        **kwargs: Any,
    ) -> CrawlResult:
        """Fetch and parse RSS feeds.

        Args:
            feeds: Dict of feed_name -> feed_url (default: DEFAULT_FEEDS).
            since: ISO date string to filter items after this date.
        """
        target_feeds = feeds or DEFAULT_FEEDS
        items: list[dict[str, Any]] = []
        errors: list[str] = []

        for feed_name, feed_url in target_feeds.items():
            await self._limiter.acquire()
            try:
                feed_items = await self._fetch_feed(feed_name, feed_url, since=since)
                items.extend(feed_items)
            except Exception as exc:
                errors.append(f"Error fetching {feed_name}: {exc}")

        logger.info("RSS crawl complete", feeds=len(target_feeds), items=len(items), errors=len(errors))
        return CrawlResult(source="rss", items=items, errors=errors)

    async def _fetch_feed(self, feed_name: str, feed_url: str, since: str = "") -> list[dict[str, Any]]:
        """Fetch and parse a single RSS feed."""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(feed_url)
            response.raise_for_status()

        root = ET.fromstring(response.text)
        items: list[dict[str, Any]] = []

        # Try RSS 2.0 format
        for item in root.findall(".//item"):
            parsed = self._parse_rss_item(item, feed_name)
            if parsed and (not since or parsed.get("published_at", "") >= since):
                items.append(parsed)

        # Try Atom format
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall(".//atom:entry", ns):
            parsed = self._parse_atom_entry(entry, feed_name, ns)
            if parsed and (not since or parsed.get("published_at", "") >= since):
                items.append(parsed)

        return items

    def _parse_rss_item(self, item: ET.Element, source: str) -> dict[str, Any] | None:
        """Parse an RSS 2.0 item."""
        title = self._text(item, "title")
        link = self._text(item, "link")
        description = self._text(item, "description")
        pub_date = self._text(item, "pubDate")

        if not title:
            return None

        return {
            "title": title.strip(),
            "url": link,
            "summary": description[:500] if description else "",
            "source": source,
            "published_at": self._parse_date(pub_date),
        }

    def _parse_atom_entry(self, entry: ET.Element, source: str, ns: dict[str, str]) -> dict[str, Any] | None:
        """Parse an Atom entry."""
        title_elem = entry.find("atom:title", ns)
        title = title_elem.text if title_elem is not None and title_elem.text else ""
        link_elem = entry.find("atom:link", ns)
        link = link_elem.get("href", "") if link_elem is not None else ""
        summary_elem = entry.find("atom:summary", ns)
        summary = summary_elem.text if summary_elem is not None and summary_elem.text else ""
        updated_elem = entry.find("atom:updated", ns)
        updated = updated_elem.text if updated_elem is not None and updated_elem.text else ""

        if not title:
            return None

        return {
            "title": title.strip(),
            "url": link,
            "summary": summary[:500],
            "source": source,
            "published_at": self._parse_date(updated),
        }

    def _text(self, elem: ET.Element, tag: str) -> str:
        """Extract text from an XML element."""
        child = elem.find(tag)
        return child.text if child is not None and child.text else ""

    def _parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format."""
        if not date_str:
            return ""
        try:
            # Try ISO format
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
        try:
            # Try RFC 2822 format (RSS)
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return date_str[:10]