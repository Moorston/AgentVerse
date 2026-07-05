"""FastAPI dependency injection — Neo4j, pgvector, and GraphRAG engine."""

from agentverse.graph_core.client import GraphClient
from agentverse.graph_core.repository.base import BaseRepository
from agentverse.graphrag.engine import GraphRAGEngine
from agentverse.shared.config import Settings
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

# Singleton instances
_client: GraphClient | None = None
_repository: BaseRepository | None = None
_engine: GraphRAGEngine | None = None


def get_settings() -> Settings:
    """Return application settings."""
    return Settings()


async def get_graph_client() -> GraphClient:
    """Return a connected GraphClient singleton."""
    global _client
    if _client is None:
        _client = GraphClient(get_settings())
        await _client.connect()
        logger.info("GraphClient singleton created")
    return _client


async def get_repository() -> BaseRepository:
    """Return a BaseRepository with connected GraphClient."""
    global _repository
    if _repository is None:
        client = await get_graph_client()
        _repository = BaseRepository(client)
        logger.info("BaseRepository singleton created")
    return _repository


async def get_graphrag_engine() -> GraphRAGEngine:
    """Return a GraphRAGEngine singleton."""
    global _engine
    if _engine is None:
        _engine = GraphRAGEngine(get_settings())
        await _engine.initialize()
        logger.info("GraphRAGEngine singleton created")
    return _engine


async def close_connections() -> None:
    """Close all database connections."""
    global _client, _repository, _engine
    if _engine:
        await _engine.close()
        _engine = None
    if _client:
        await _client.close()
        _client = None
        _repository = None
    logger.info("All database connections closed")