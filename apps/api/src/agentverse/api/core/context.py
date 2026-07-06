"""Application-wide dependency container (AppContext)."""

from __future__ import annotations

from fastapi import Request

from agentverse.graph_core.client import GraphClient
from agentverse.graph_core.repository.base import BaseRepository
from agentverse.graphrag.engine import GraphRAGEngine
from agentverse.shared.config import Settings
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


class AppContext:
    """Lazily-initialised container for expensive singletons.

    Created once at startup and stored on ``app.state.context``.
    Individual resources are connected on first access so that import
    time stays fast and optional backends (Neo4j, pgvector) can be
    absent without breaking startup.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: GraphClient | None = None
        self._repository: BaseRepository | None = None
        self._engine: GraphRAGEngine | None = None

    # -- Accessors (lazy-init) ------------------------------------------

    async def get_client(self) -> GraphClient:
        """Return a connected GraphClient, creating it on first call."""
        if self._client is None:
            self._client = GraphClient(self._settings)
            await self._client.connect()
            logger.info("GraphClient created via AppContext")
        return self._client

    async def get_repository(self) -> BaseRepository:
        """Return a BaseRepository backed by the shared GraphClient."""
        if self._repository is None:
            client = await self.get_client()
            self._repository = BaseRepository(client)
            logger.info("BaseRepository created via AppContext")
        return self._repository

    async def get_engine(self) -> GraphRAGEngine:
        """Return a GraphRAGEngine, initialising it on first call."""
        if self._engine is None:
            self._engine = GraphRAGEngine(self._settings)
            await self._engine.initialize()
            logger.info("GraphRAGEngine created via AppContext")
        return self._engine

    # -- Teardown -------------------------------------------------------

    async def close(self) -> None:
        """Tear down all managed resources in safe order."""
        if self._engine:
            await self._engine.close()
            self._engine = None
        if self._client:
            await self._client.close()
            self._client = None
            self._repository = None
        logger.info("AppContext resources closed")


# ------------------------------------------------------------------
# FastAPI dependency helper
# ------------------------------------------------------------------

async def get_context(request: Request) -> AppContext:
    """FastAPI Depends-compatible accessor for the AppContext."""
    ctx: AppContext = request.app.state.context
    return ctx
