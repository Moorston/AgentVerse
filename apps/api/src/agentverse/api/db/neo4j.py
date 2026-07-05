"""Neo4j async session management with connection pooling.

Provides a singleton `Neo4jManager` that wraps the official neo4j async driver,
exposing health-check, graceful shutdown, and a convenience `execute_read` / `execute_write`
API for use inside FastAPI lifespan events.
"""

from __future__ import annotations

import asyncio
from typing import Any, TypeVar

from neo4j import AsyncDriver, AsyncGraphDatabase, AsyncSession
from neo4j.exceptions import ServiceUnavailable

from agentverse.shared.config import Settings
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")

# ─── Retry configuration ──────────────────────────────────────────────

MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 0.5  # seconds; doubles each attempt


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


class Neo4jManager:
    """Async Neo4j connection manager with pooling and health checks.

    Usage (inside FastAPI lifespan):

        neo4j = Neo4jManager.from_settings(settings)
        await neo4j.connect()
        yield
        await neo4j.close()
    """

    def __init__(
        self,
        uri: str,
        user: str,
        password: str,
        *,
        max_connection_pool_size: int = 50,
        connection_acquisition_timeout: float = 60.0,
        max_transaction_retry_time: float = 30.0,
    ) -> None:
        self._uri = uri
        self._user = user
        self._password = password
        self._pool_size = max_connection_pool_size
        self._acquisition_timeout = connection_acquisition_timeout
        self._retry_time = max_transaction_retry_time
        self._driver: AsyncDriver | None = None

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> "Neo4jManager":
        """Create a manager from application settings."""
        if settings is None:
            settings = Settings()
        return cls(
            uri=settings.neo4j_uri,
            user=settings.neo4j_user,
            password=settings.neo4j_password,
        )

    # ─── Lifecycle ─────────────────────────────────────────────────────

    async def connect(self) -> None:
        """Initialize the async driver and verify connectivity."""
        self._driver = AsyncGraphDatabase.driver(
            self._uri,
            auth=(self._user, self._password),
            max_connection_pool_size=self._pool_size,
            connection_acquisition_timeout=self._acquisition_timeout,
            max_transaction_retry_time=self._retry_time,
        )
        # Verify the connection is actually alive
        await _retry(lambda: self._driver.verify_connectivity(), label="verify_connectivity")
        logger.info(
            "neo4j_connected",
            uri=self._uri,
            pool_size=self._pool_size,
        )

    async def close(self) -> None:
        """Gracefully close the driver and all pooled connections."""
        if self._driver:
            await self._driver.close()
            self._driver = None
            logger.info("neo4j_disconnected")

    async def health_check(self) -> dict[str, Any]:
        """Return connectivity status with basic DB stats."""
        if not self._driver:
            return {"status": "error", "detail": "Driver not initialized"}
        try:
            async with self._driver.session() as session:
                result = await session.run("RETURN 1 AS ping")
                record = await result.single()
                if record and record["ping"] == 1:
                    return {"status": "ok"}
            return {"status": "error", "detail": "Unexpected response"}
        except Exception as exc:
            logger.error("neo4j_health_check_failed", error=str(exc))
            return {"status": "error", "detail": str(exc)}

    # ─── Query helpers ─────────────────────────────────────────────────

    @property
    def driver(self) -> AsyncDriver:
        """Access the underlying driver (for advanced use)."""
        if not self._driver:
            raise RuntimeError("Neo4jManager not connected. Call connect() first.")
        return self._driver

    def session(self, **kwargs: Any) -> AsyncSession:
        """Open a new async session from the pool.

        Typical usage:
            async with neo4j.session() as session:
                result = await session.run("MATCH (n) RETURN count(n)")
        """
        return self.driver.session(**kwargs)

    async def execute_read(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute a read transaction and return results as list of dicts."""
        async with self.session() as session:
            result = await session.execute_read(
                lambda tx: _run_and_collect(tx, query, params or {})
            )
            return result

    async def execute_write(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute a write transaction and return results as list of dicts."""
        async with self.session() as session:
            result = await session.execute_write(
                lambda tx: _run_and_collect(tx, query, params or {})
            )
            return result


# ─── Internal helpers ──────────────────────────────────────────────────

async def _run_and_collect(tx, query: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    """Run a query in a transaction and collect all records as dicts."""
    result = await tx.run(query, **params)
    records = await result.data()
    return records
