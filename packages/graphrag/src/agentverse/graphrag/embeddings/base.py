"""Embedding model abstraction."""

from abc import ABC, abstractmethod


class BaseEmbeddingModel(ABC):
    """Abstract base for embedding models."""

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Embed a single text string."""

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of text strings."""