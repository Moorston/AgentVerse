"""Base crawler abstraction."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CrawlResult:
    """Result from a crawler run."""
    source: str
    items: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class BaseCrawler(ABC):
    """Abstract base for all crawlers."""

    @abstractmethod
    async def crawl(self, **kwargs) -> CrawlResult:
        """Execute a crawl and return results."""