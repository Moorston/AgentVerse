"""PgVectorStore — pgvector-backed vector storage and similarity search."""

from __future__ import annotations

from typing import Any

import asyncpg

from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


class PgVectorStore:
    """Vector similarity search backed by PostgreSQL + pgvector.

    Uses cosine distance (<=>) for similarity search.
    Embeddings are stored in the ``embeddings`` table.
    """

    def __init__(
        self,
        dsn: str,
        table: str = "embeddings",
        vector_dim: int = 1536,
        pool_min: int = 1,
        pool_max: int = 10,
    ) -> None:
        self._dsn = dsn
        self._table = table
        self._vector_dim = vector_dim
        self._pool_min = pool_min
        self._pool_max = pool_max
        self._pool: asyncpg.Pool | None = None

    # ── Lifecycle ──────────────────────────────────────────────────

    async def connect(self) -> None:
        """Open the connection pool and ensure schema exists."""
        self._pool = await asyncpg.create_pool(
            self._dsn,
            min_size=self._pool_min,
            max_size=self._pool_max,
        )
        await self._ensure_schema()
        logger.info(
            "PgVectorStore connected",
            table=self._table,
            dim=self._vector_dim,
        )

    async def close(self) -> None:
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
        logger.info("PgVectorStore closed")

    async def _ensure_schema(self) -> None:
        """Create the extension and table if they do not exist."""
        assert self._pool
        async with self._pool.acquire() as conn:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self._table} (
                    id          TEXT PRIMARY KEY,
                    embedding   vector({self._vector_dim}) NOT NULL,
                    content     TEXT NOT NULL DEFAULT '',
                    metadata    JSONB NOT NULL DEFAULT '{{}}',
                    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)

            # HNSW index for fast approximate nearest-neighbour search
            await conn.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{self._table}_hnsw
                ON {self._table}
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64)
            """)

    # ── CRUD ───────────────────────────────────────────────────────

    async def upsert(self, id: str, embedding: list[float], content: str = "", metadata: dict[str, Any] | None = None) -> None:
        """Insert or update a row by id."""
        assert self._pool
        async with self._pool.acquire() as conn:
            await conn.execute(
                f"""
                INSERT INTO {self._table} (id, embedding, content, metadata, created_at)
                VALUES ($1, $2::vector, $3, $4::jsonb, now())
                ON CONFLICT (id)
                DO UPDATE SET
                    embedding = $2::vector,
                    content   = $3,
                    metadata  = $4::jsonb,
                    created_at = now()
                """,
                id,
                embedding,
                content,
                metadata or {},
            )

    async def delete(self, *ids: str) -> int:
        """Delete one or more rows by id. Returns the number of deleted rows."""
        assert self._pool
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                f"DELETE FROM {self._table} WHERE id = ANY($1::text[])",
                list(ids),
            )
            # result is a string like "DELETE 3"
            return int(result.split()[-1]) if result else 0

    async def count(self) -> int:
        """Return the total number of stored embeddings."""
        assert self._pool
        async with self._pool.acquire() as conn:
            row = await conn.fetchval(f"SELECT count(*) FROM {self._table}")
        return row or 0

    # ── Search ─────────────────────────────────────────────────────

    async def search(
        self,
        query_embedding: list[float],
        *,
        top_k: int = 10,
        offset: int = 0,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Return the top-k most similar rows, ordered by cosine distance (ascending)."""
        assert self._pool
        where = ""
        params: list[Any] = [query_embedding, top_k, offset]
        if metadata_filter:
            where = "AND metadata @> $4::jsonb"
            params.append(metadata_filter)

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT
                    id,
                    content,
                    metadata,
                    created_at,
                    1 - (embedding <=> $1::vector) AS similarity
                FROM {self._table}
                WHERE 1=1 {where}
                ORDER BY embedding <=> $1::vector
                LIMIT $2 OFFSET $3
                """,
                *params,
            )
        return [
            {
                "id": r["id"],
                "content": r["content"],
                "metadata": r["metadata"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                "score": round(float(r["similarity"]), 4),
            }
            for r in rows
        ]

    async def search_by_text(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        offset: int = 0,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search using full-text (ILUKE) rather than vector similarity.

        Useful as a fallback when no embedding model is available.
        """
        assert self._pool
        # Simple trigram-like search via ILIKE
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT
                    id,
                    content,
                    metadata,
                    created_at
                FROM {self._table}
                WHERE content ILIKE $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
                """,
                f"%{query_text}%",
                top_k,
                offset,
            )
        return [
            {
                "id": r["id"],
                "content": r["content"],
                "metadata": r["metadata"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                "score": 0.0,
            }
            for r in rows
        ]