"""OpenAI embedding model adapter."""

from typing import Any

from agentverse.graphrag.embeddings.base import BaseEmbeddingModel
from agentverse.shared.config import Settings
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


class OpenAIEmbeddingModel(BaseEmbeddingModel):
    """OpenAI embedding model adapter."""

    def __init__(self, api_key: str = "", model: str = "text-embedding-3-small", dimension: int = 1536) -> None:
        self._api_key = api_key
        self._model = model
        self._dimension = dimension

    async def embed(self, text: str) -> list[float]:
        """Embed text via OpenAI API."""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self._api_key)
        response = await client.embeddings.create(
            input=text,
            model=self._model,
            dimensions=self._dimension,
        )
        return response.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed batch via OpenAI API."""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self._api_key)
        response = await client.embeddings.create(
            input=texts,
            model=self._model,
            dimensions=self._dimension,
        )
        # Sort by index to maintain order
        sorted_data = sorted(response.data, key=lambda x: x.index)
        return [item.embedding for item in sorted_data]