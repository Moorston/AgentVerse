"""Health check endpoint with full system status."""

from fastapi import APIRouter

from agentverse.api.core.cache import query_cache, concept_cache
from agentverse.api.core.query_monitor import get_query_stats
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Return comprehensive service health status.

    Returns:
        - Service status and version
        - Neo4j connection status
        - PostgreSQL connection status
        - Cache statistics
    """
    health = {
        "status": "ok",
        "version": "0.1.0",
        "services": {},
        "cache": {},
    }

    # Check Neo4j
    try:
        from agentverse.api.core.dependencies import get_graph_client
        client = await get_graph_client()
        neo4j_ok = await client.health_check()
        node_count = await client.node_count()
        rel_count = await client.relationship_count()
        health["services"]["neo4j"] = {
            "status": "ok" if neo4j_ok else "unavailable",
            "nodes": node_count,
            "relationships": rel_count,
        }
    except Exception as exc:
        health["services"]["neo4j"] = {"status": "unavailable", "error": str(exc)[:100]}

    # Check pgvector
    try:
        from agentverse.api.db.postgres import VectorStore
        from agentverse.shared.config import Settings
        settings = Settings()
        store = VectorStore(dsn=settings.postgres_dsn)
        await store.connect()
        pg_ok = await store.health_check()
        embed_count = await store.count()
        health["services"]["pgvector"] = {
            "status": "ok" if pg_ok else "unavailable",
            "embeddings": embed_count,
        }
        await store.close()
    except Exception as exc:
        health["services"]["pgvector"] = {"status": "unavailable", "error": str(exc)[:100]}

    # Cache stats
    health["cache"] = {
        "query_cache": query_cache.stats(),
        "concept_cache": concept_cache.stats(),
    }

    # Query performance stats
    health["query_stats"] = get_query_stats()

    # Overall status
    all_ok = all(
        svc.get("status") == "ok"
        for svc in health["services"].values()
    )
    health["status"] = "ok" if all_ok else "degraded"

    return health