"""GraphRAG engine — top-level entry point for hybrid retrieval."""

from typing import Any

from agentverse.graph_core.client import GraphClient
from agentverse.graphrag.embeddings.base import BaseEmbeddingModel
from agentverse.graphrag.embeddings.models import OpenAIEmbeddingModel
from agentverse.graphrag.indexing.pipeline import IndexingPipeline
from agentverse.graphrag.retrieval.graph import GraphSearch
from agentverse.graphrag.retrieval.hybrid import HybridSearch
from agentverse.graphrag.retrieval.pgvector_store import PgVectorStore
from agentverse.graphrag.retrieval.vector import VectorSearch
from agentverse.shared.config import Settings
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


class GraphRAGEngine:
    """Graph-augmented retrieval-augmented generation engine.

    Combines vector similarity search (pgvector) with knowledge graph
    traversal (Neo4j) for high-quality retrieval.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or Settings()
        self._client = GraphClient(self._settings)
        self._embedding_model: BaseEmbeddingModel | None = None
        self._vector_store: PgVectorStore | None = None
        self._vector_search: VectorSearch | None = None
        self._graph_search: GraphSearch | None = None
        self._hybrid_search: HybridSearch | None = None
        self._indexing_pipeline: IndexingPipeline | None = None

    async def initialize(self) -> None:
        """Initialize database connections and search engines."""
        # Neo4j
        await self._client.connect()
        if await self._client.health_check():
            logger.info("Neo4j connected")
        else:
            logger.warning("Neo4j not available")

        # Embedding model
        self._embedding_model = OpenAIEmbeddingModel(
            api_key=self._settings.openai_api_key,
            model=self._settings.embedding_model,
            dimension=self._settings.embedding_dimension,
        )

        # Vector search (pgvector)
        self._vector_store = PgVectorStore(dsn=self._settings.postgres_dsn, vector_dim=self._settings.embedding_dimension)
        try:
            await self._vector_store.connect()
            logger.info("PgVectorStore connected")
        except Exception as exc:
            logger.warning("PgVectorStore not available", error=str(exc))

        self._vector_search = VectorSearch(
            embedding_model=self._embedding_model,
            store=self._vector_store,
        )
        await self._vector_search.initialize()

        # Graph search (Neo4j)
        self._graph_search = GraphSearch(self._client)

        # Hybrid search
        self._hybrid_search = HybridSearch(self._vector_search, self._graph_search)

        # Indexing pipeline
        self._indexing_pipeline = IndexingPipeline(
            self._embedding_model, self._client, vector_store=self._vector_store
        )

        logger.info("GraphRAG engine initialized")

    async def close(self) -> None:
        """Close all connections."""
        await self._client.close()
        if self._vector_store:
            await self._vector_store.close()
        logger.info("GraphRAG engine closed")

    async def query(
        self,
        text: str,
        top_k: int = 10,
        strategy: str = "hybrid",
    ) -> list[dict[str, Any]]:
        """Execute a GraphRAG query.

        Args:
            text: Query text.
            top_k: Maximum results.
            strategy: "hybrid", "vector", or "graph".

        Returns:
            Ranked list of results.
        """
        if strategy == "vector" and self._vector_search:
            return await self._vector_search.search(text, top_k)
        elif strategy == "graph" and self._graph_search:
            return await self._graph_search.search(text, top_k)
        elif self._hybrid_search:
            return await self._hybrid_search.search(text, top_k)
        else:
            logger.warning("GraphRAG engine not fully initialized")
            return []

    async def reindex(self, labels: list[str] | None = None) -> int:
        """Reindex all nodes into pgvector."""
        if not self._indexing_pipeline:
            raise RuntimeError("GraphRAGEngine not initialized.")
        return await self._indexing_pipeline.run(labels=labels)

    @property
    def graph_client(self) -> GraphClient:
        """Access the underlying GraphClient."""
        return self._client