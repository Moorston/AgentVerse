"""Application lifespan events (startup / shutdown)."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from agentverse.api.core.context import AppContext
from agentverse.graph_core.schema.constraints import apply_constraints
from agentverse.graph_core.schema.indexes import apply_indexes
from agentverse.shared.config import Settings
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifecycle via AppContext."""
    logger.info("api_startup")

    # Reuse context if already created by create_app(), otherwise create one.
    context: AppContext = getattr(app.state, "context", None)
    if context is None:
        settings = Settings()
        context = AppContext(settings)
        app.state.context = context

    # Probe Neo4j and apply schema if available
    try:
        client = await context.get_client()
        healthy = await client.health_check()
        if healthy:
            logger.info("neo4j_connection_healthy")
            await apply_constraints(client)
            await apply_indexes(client)
            logger.info("neo4j_schema_applied")
        else:
            logger.warning("neo4j_unavailable", detail="running without database")
    except Exception as exc:
        logger.warning("neo4j_connection_failed", error=str(exc), detail="running without database")

    yield

    logger.info("api_shutdown")
    await context.close()
