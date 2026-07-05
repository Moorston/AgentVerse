"""Application lifespan events (startup / shutdown)."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from agentverse.api.core.dependencies import get_graph_client, close_connections
from agentverse.graph_core.schema.constraints import apply_constraints
from agentverse.graph_core.schema.indexes import apply_indexes
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifecycle."""
    logger.info("api_startup")

    # Initialize database connections
    try:
        client = await get_graph_client()
        healthy = await client.health_check()
        if healthy:
            logger.info("neo4j_connection_healthy")
            # Apply schema on startup
            await apply_constraints(client)
            await apply_indexes(client)
            logger.info("neo4j_schema_applied")
        else:
            logger.warning("neo4j_unavailable", detail="running without database")
    except Exception as exc:
        logger.warning("neo4j_connection_failed", error=str(exc), detail="running without database")

    yield

    logger.info("api_shutdown")
    await close_connections()
