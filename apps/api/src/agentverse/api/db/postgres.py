"""PostgreSQL connection pool with pgvector support."""

from typing import Any

from agentverse.shared.config import Settings
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

# SQL schema for pgvector
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS node_embeddings (
    id           SERIAL PRIMARY KEY,
    node_id      TEXT NOT NULL,
    node_label   TEXT NOT NULL,
    content      TEXT NOT NULL,
    embedding    vector(1536) NOT NULL,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    updated_at   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(node_id)
);

CREATE INDEX IF NOT EXISTS idx_embeddings_cosine
    ON node_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_embeddings_label
    ON node_embeddings (node_label);
"""

UPSERT_SQL = """
INSERT INTO node_embeddings (node_id, node_label, content, embedding, updated_at)
VALUES ($1, $2, $3, $4::vector, NOW())
ON CONFLICT (node_id)
DO UPDATE SET content = $3, embedding = $4::vector, updated_at = NOW()
"""

SEARCH_SQL = """
SELECT node_id, node_label, content,
       1 - (embedding <=> $1::vector) AS similarity
FROM node_embeddings
ORDER BY embedding <=> $1::vector
LIMIT $2
"""

COUNT_SQL = "SELECT COUNT(*) AS cnt FROM node_embeddings"
DELETE_SQL = "DELETE FROM node_embeddings WHERE node_id = $1"


class VectorStore:
    """PostgreSQL + pgvector vector store."""

    def __init__(self, dsn: str = "", dimension: int = 1536) -> None:
        self._dsn = dsn
        self._dimension = dimension
        self._pool: Any = None

    async def connect(self) -> None:
        """Initialize the connection pool."""
        import asyncpg

        self._pool = await asyncpg.create_pool(self._dsn, min_size=2, max_size=10)
        logger.info("PostgreSQL connection pool created")

        # Ensure table exists
        async with self._pool.acquire() as conn:
            await conn.execute(CREATE_TABLE_SQL)
        logger.info("pgvector schema initialized")

    async def close(self) -> None:
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            logger.info("PostgreSQL connection pool closed")

    async def health_check(self) -> bool:
        """Check if the database connection is healthy."""
        if not self._pool:
            return False
        try:
            async with self._pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as exc:
            logger.error("PostgreSQL health check failed", error=str(exc))
            return False

    async def upsert(self, node_id: str, node_label: str, content: str, embedding: list[float]) -> None:
        """Insert or update a node embedding."""
        if not self._pool:
            raise RuntimeError("VectorStore not connected")

        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
        async with self._pool.acquire() as conn:
            await conn.execute(UPSERT_SQL, node_id, node_label, content, embedding_str)

    async def search(self, query_embedding: list[float], top_k: int = 10) -> list[dict[str, Any]]:
        """Search for similar embeddings using cosine distance."""
        if not self._pool:
            raise RuntimeError("VectorStore not connected")

        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(SEARCH_SQL, embedding_str, top_k)

        return [
            {
                "node_id": row["node_id"],
                "node_label": row["node_label"],
                "content": row["content"],
                "similarity": float(row["similarity"]),
            }
            for row in rows
        ]

    async def count(self) -> int:
        """Count total embeddings."""
        if not self._pool:
            return 0
        async with self._pool.acquire() as conn:
            return await conn.fetchval(COUNT_SQL)

    async def delete(self, node_id: str) -> None:
        """Delete an embedding by node_id."""
        if not self._pool:
            raise RuntimeError("VectorStore not connected")
        async with self._pool.acquire() as conn:
            await conn.execute(DELETE_SQL, node_id)