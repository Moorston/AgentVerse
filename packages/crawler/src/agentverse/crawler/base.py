"""Base crawler abstraction."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from agentverse.crawler.types import CrawlRequest


@dataclass
class CrawlResult:
    """Result from a crawler run."""
    source: str
    items: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class BaseCrawler(ABC):
    """Abstract base for all crawlers."""

    @abstractmethod
    async def crawl(self, request: CrawlRequest | None = None) -> CrawlResult:
        """Execute a crawl and return results.

        Args:
            request: Structured request parameters.
        """