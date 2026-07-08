"""Neo4j driver wrapper for async operations with retry support."""

from typing import Any

from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from neo4j.exceptions import ServiceUnavailable

from agentverse.shared.config import Settings
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 0.5  # seconds; doubles each attempt

import asyncio


async def _retry(coro_factory, *, max_retries: int = MAX_RETRIES, label: str = "operation") -> Any:
    """Execute an async callable with exponential backoff on ServiceUnavailable."""
    last_exc: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            return await coro_factory()
        except ServiceUnavailable as exc:
            last_exc = exc
            wait = RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
            logger.warning(
                "neo4j_retry",
                label=label,
                attempt=attempt,
                max_retries=max_retries,
                wait_seconds=round(wait, 2),
                error=str(exc),
            )
            if attempt < max_retries:
                await asyncio.sleep(wait)
    raise last_exc  # type: ignore[misc]


class GraphClient:
    """Async Neo4j client wrapper with connection retry support."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or Settings()
        self._driver: AsyncDriver | None = None

    async def connect(self) -> None:
        """Initialize the Neo4j driver and verify connectivity."""
        self._driver = AsyncGraphDatabase.driver(
            self._settings.neo4j_uri,
            auth=(self._settings.neo4j_user, self._settings.neo4j_password),
        )
        await _retry(lambda: self._driver.verify_connectivity(), label="verify_connectivity")
        logger.info("Neo4j driver initialized", uri=self._settings.neo4j_uri)

    async def close(self) -> None:
        """Close the Neo4j driver."""
        if self._driver:
            await self._driver.close()
            logger.info("Neo4j driver closed")

    def session(self) -> AsyncSession:
        """Return a new async session."""
        if not self._driver:
            raise RuntimeError("GraphClient not connected. Call connect() first.")
        return self._driver.session()

    async def health_check(self) -> bool:
        """Check if the Neo4j connection is healthy."""
        if not self._driver:
            return False
        try:
            async with self.session() as session:
                result = await session.run("RETURN 1 AS ok")
                record = await result.single()
                return record["ok"] == 1
        except Exception as exc:
            logger.error("Neo4j health check failed", error=str(exc))
            return False

    async def node_count(self, label: str | None = None) -> int:
        """Count nodes, optionally filtered by label."""
        cql = f"MATCH (n:{label}) RETURN count(n) AS cnt" if label else "MATCH (n) RETURN count(n) AS cnt"
        async with self.session() as session:
            result = await session.run(cql)
            record = await result.single()
            return record["cnt"]

    async def relationship_count(self) -> int:
        """Count all relationships."""
        async with self.session() as session:
            result = await session.run("MATCH ()-[r]->() RETURN count(r) AS cnt")
            record = await result.single()
            return record["cnt"]

    async def execute(self, cql: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute a Cypher query and return records."""
        async with self.session() as session:
            result = await session.run(cql, parameters or {})
            return [record.data() for record in await result.fetch()]