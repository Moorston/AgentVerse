"""Framework ecosystem endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, Query

from agentverse.api.core.dependencies import get_repository
from agentverse.graph_core.repository.base import BaseRepository
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/")
async def list_frameworks(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    repo: BaseRepository = Depends(get_repository),
) -> list[dict[str, Any]]:
    """List all frameworks in the knowledge graph."""
    offset = (page - 1) * size
    results = await repo.execute_raw(
        """
        MATCH (f:Framework)
        OPTIONAL MATCH (f)-[r:IMPLEMENTS]->(c:Concept)
        RETURN f.name AS name, f.description AS description, f.stars AS stars,
               collect(c.name) AS implements
        SKIP $offset LIMIT $limit
        """,
        {"offset": offset, "limit": size},
    )
    return [dict(r) for r in results]


@router.get("/{name}")
async def get_framework(
    name: str,
    repo: BaseRepository = Depends(get_repository),
) -> dict[str, Any]:
    """Get framework details with all relationships."""
    results = await repo.execute_raw(
        """
        MATCH (f:Framework {name: $name})
        OPTIONAL MATCH (f)-[r]-(m)
        RETURN f, collect({rel: type(r), target: m.name, labels: labels(m)}) AS connections
        """,
        {"name": name},
    )
    if not results:
        return {"error": f"Framework '{name}' not found", "name": name}

    record = results[0]
    fw = record.get("f", {})
    return {
        "name": fw.get("name", name),
        "description": fw.get("description", ""),
        "stars": fw.get("stars", 0),
        "connections": record.get("connections", []),
    }