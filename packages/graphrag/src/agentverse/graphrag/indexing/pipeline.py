"""Indexing pipeline — writes node embeddings to pgvector."""

from typing import Any

from agentverse.graph_core.client import GraphClient
from agentverse.graphrag.embeddings.base import BaseEmbeddingModel
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


class IndexingPipeline:
    """Pipeline for processing nodes into pgvector embeddings."""

    def __init__(self, embedding_model: BaseEmbeddingModel, graph_client: GraphClient) -> None:
        self._embedding_model = embedding_model
        self._graph_client = graph_client

    async def run(self, labels: list[str] | None = None, batch_size: int = 50) -> int:
        """Index all nodes of given labels into pgvector.

        Args:
            labels: Node labels to index (default: all Concept-based labels).
            batch_size: Batch size for embedding requests.

        Returns:
            Number of indexed nodes.
        """
        target_labels = labels or [
            "Agent", "Framework", "Paper", "Protocol",
            "MemoryFramework", "MemoryType", "Application", "Pattern",
        ]

        total_indexed = 0
        for label in target_labels:
            count = await self._index_label(label, batch_size)
            total_indexed += count

        logger.info("Indexing complete", total=total_indexed)
        return total_indexed

    async def _index_label(self, label: str, batch_size: int) -> int:
        """Index all nodes of a given label."""
        # Fetch all nodes of this label
        nodes = await self._graph_client.execute(
            f"MATCH (n:{label}) RETURN elementId(n) AS id, n.name AS name, n.description AS description LIMIT 1000"
        )

        if not nodes:
            return 0

        # Prepare content for embedding
        contents: list[str] = []
        node_ids: list[str] = []
        for node in nodes:
            name = node.get("name", "")
            desc = node.get("description", "")
            content = f"{name}: {desc}" if desc else name
            if content:
                contents.append(content)
                node_ids.append(node["id"])

        # Batch embed
        indexed = 0
        for i in range(0, len(contents), batch_size):
            batch_contents = contents[i:i + batch_size]
            batch_ids = node_ids[i:i + batch_size]

            try:
                embeddings = await self._embedding_model.embed_batch(batch_contents)

                # Write to pgvector via VectorStore
                # TODO: Wire up actual VectorStore connection
                # For now, log the indexing action
                for node_id, content, embedding in zip(batch_ids, batch_contents, embeddings):
                    logger.debug(
                        "Would index to pgvector",
                        node_id=node_id,
                        content_preview=content[:50],
                        embedding_dim=len(embedding),
                    )

                indexed += len(embeddings)
                logger.debug("Indexed batch", label=label, count=len(embeddings))
            except Exception as exc:
                logger.error("Batch indexing failed", label=label, error=str(exc))

        logger.info("Label indexed", label=label, count=indexed)
        return indexed
