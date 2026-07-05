"""Vector similarity search via pgvector — connected to VectorStore."""

from typing import Any

from agentverse.graphrag.embeddings.base import BaseEmbeddingModel
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


class VectorSearch:
    """Vector similarity search using pgvector."""

    def __init__(self, embedding_model: BaseEmbeddingModel, dsn: str = "") -> None:
        self._embedding_model = embedding_model
        self._dsn = dsn
        self._store: Any = None

    async def initialize(self) -> None:
        """Initialize the vector store connection."""
        try:
            from agentverse.api.db.postgres import VectorStore
            self._store = VectorStore(dsn=self._dsn, dimension=1536)
            await self._store.connect()
            logger.info("VectorSearch initialized with pgvector")
        except Exception as exc:
            logger.warning("VectorSearch pgvector not available", error=str(exc))
            self._store = None

    async def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """Search for semantically similar content.

        Args:
            query: Search query text.
            top_k: Maximum number of results.

        Returns:
            List of results with node_id, content, similarity score.
        """
        if not self._store:
            logger.warning("VectorSearch not available — returning empty results")
            return []

        query_embedding = await self._embedding_model.embed(query)
        results = await self._store.search(query_embedding, top_k=top_k)

        logger.info("Vector search complete", query_len=len(query), results=len(results))
        return results

    async def index_node(self, node_id: str, content: str, label: str = "Concept") -> list[float]:
        """Embed and index a single node.

        Args:
            node_id: Neo4j element_id.
            content: Text content to embed.
            label: Node label.

        Returns:
            The embedding vector.
        """
        embedding = await self._embedding_model.embed(content)
        if self._store:
            await self._store.upsert(node_id, label, content, embedding)
            logger.debug("Indexed node", node_id=node_id, dim=len(embedding))
        return embedding