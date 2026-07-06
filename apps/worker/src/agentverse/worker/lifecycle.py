"""Worker lifecycle — manage database client initialization and teardown.

Unlike the API (which uses FastAPI lifespan), the Worker is a standalone
async process and needs its own client management.
"""

from __future__ import annotations

from dataclasses import dataclass

from agentverse.graph_core.client import GraphClient
from agentverse.graphrag.retrieval.pgvector_store import PgVectorStore
from agentverse.shared.config import Settings
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


@dataclass
class WorkerClients:
    """Holds all database clients the Worker needs."""
    graph: GraphClient
    vector_store: PgVectorStore | None


async def init_clients(settings: Settings | None = None) -> WorkerClients:
    """Create and connect all database clients.

    Returns a ``WorkerClients`` instance with a connected ``GraphClient``
    and, when a PostgreSQL DSN is configured, a connected ``PgVectorStore``.
    """
    settings = settings or Settings()
    logger.info("worker_clients_init")

    graph = GraphClient(settings)
    await graph.connect()
    healthy = await graph.health_check()
    if healthy:
        logger.info("neo4j_connected")
    else:
        logger.warning("neo4j_unavailable")

    vector_store: PgVectorStore | None = None
    if settings.postgres_dsn:
        try:
            vector_store = PgVectorStore(dsn=settings.postgres_dsn)
            await vector_store.connect()
            logger.info("pgvector_connected")
        except Exception as exc:
            logger.warning("pgvector_unavailable", error=str(exc))
            vector_store = None

    return WorkerClients(graph=graph, vector_store=vector_store)


async def close_clients(clients: WorkerClients) -> None:
    """Gracefully close all database connections."""
    logger.info("worker_clients_shutdown")
    if clients.vector_store:
        await clients.vector_store.close()
    await clients.graph.close()
