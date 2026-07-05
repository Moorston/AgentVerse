"""Base extractor abstraction."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExtractionResult:
    """Result from an extraction run."""
    source: str
    entities: list[dict[str, Any]] = field(default_factory=list)
    relationships: list[dict[str, Any]] = field(default_factory=list)


class BaseExtractor(ABC):
    """Abstract base for all extractors."""

    @abstractmethod
    async def extract(self, text: str, **kwargs) -> ExtractionResult:
        """Extract structured information from text."""