"""Concept CRUD endpoints — with pagination metadata and query monitoring."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from agentverse.api.core.dependencies import get_repository
from agentverse.api.core.query_monitor import monitor_query
from agentverse.api.models.request import ConceptCreate
from agentverse.api.models.response import ConceptResponse, GraphDataResponse
from agentverse.api.models.pagination import PaginatedResponse
from agentverse.graph_core.repository.base import BaseRepository
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/")
@monitor_query("list_concepts")
async def list_concepts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: str = Query("", description="Filter by category"),
    repo: BaseRepository = Depends(get_repository),
) -> PaginatedResponse:
    """List all concepts in the knowledge graph with pagination metadata."""
    offset = (page - 1) * size

    # Count total
    if category:
        count_result = await repo.run(_query(
            "MATCH (n:Concept {category: $category}) RETURN count(n) AS total",
            {"category": category},
        ))
    else:
        count_result = await repo.run(_query(
            "MATCH (n:Concept) RETURN count(n) AS total",
            {},
        ))
    total = count_result[0]["total"] if count_result else 0

    # Fetch page
    if category:
        results = await repo.run(_query(
            """
            MATCH (n:Concept {category: $category})
            RETURN n.name AS name, n.description AS description, n.category AS category
            SKIP $offset LIMIT $limit
            """,
            {"category": category, "offset": offset, "limit": size},
        ))
    else:
        results = await repo.run(_query(
            """
            MATCH (n:Concept)
            RETURN n.name AS name, n.description AS description, n.category AS category
            SKIP $offset LIMIT $limit
            """,
            {"offset": offset, "limit": size},
        ))

    items = [ConceptResponse(**r).model_dump() for r in results]
    return PaginatedResponse.create(items=items, page=page, size=size, total=total)


@router.get("/{name}", response_model=ConceptResponse)
@monitor_query("get_concept")
async def get_concept(
    name: str,
    repo: BaseRepository = Depends(get_repository),
) -> ConceptResponse:
    """Get a specific concept by name."""
    result = await repo.find_node("Concept", name)
    if not result:
        raise HTTPException(status_code=404, detail=f"Concept '{name}' not found")
    node = result.get("n", {})
    return ConceptResponse(
        name=node.get("name", name),
        description=node.get("description", ""),
        category=node.get("category", ""),
    )


@router.get("/{name}/neighbors", response_model=GraphDataResponse)
@monitor_query("get_neighbors")
async def get_neighbors(
    name: str,
    depth: int = Query(1, ge=1, le=5),
    repo: BaseRepository = Depends(get_repository),
) -> GraphDataResponse:
    """Get N-hop neighbors of a concept as a subgraph."""
    cql = f"""
    MATCH path = (n:Concept {{name: $name}})-[*1..{depth}]-(m)
    RETURN nodes(path) AS ns, relationships(path) AS rs
    LIMIT 100
    """
    results = await repo.run(_query(cql, {"name": name}))

    nodes = []
    edges = []
    seen_nodes: set[str] = set()
    seen_edges: set[str] = set()

    for record in results:
        for node in record.get("ns", []):
            node_id = str(node.get("elementId", node.get("name", "")))
            if node_id not in seen_nodes:
                seen_nodes.add(node_id)
                labels = node.get("labels", [])
                nodes.append({
                    "id": node_id,
                    "label": node.get("name", ""),
                    "type": labels[0] if labels else "Concept",
                    "properties": dict(node),
                })
        for rel in record.get("rs", []):
            rel_id = str(rel.get("elementId", ""))
            if rel_id not in seen_edges:
                seen_edges.add(rel_id)
                edges.append({
                    "id": rel_id,
                    "source": str(rel.get("startNode", "")),
                    "target": str(rel.get("endNode", "")),
                    "type": rel.get("type", "RELATED_TO"),
                    "properties": dict(rel),
                })

    return GraphDataResponse(nodes=nodes, edges=edges)


@router.post("/", response_model=ConceptResponse)
@monitor_query("create_concept")
async def create_concept(
    data: ConceptCreate,
    repo: BaseRepository = Depends(get_repository),
) -> ConceptResponse:
    """Create a new concept."""
    await repo.create_node(
        labels=["Concept"],
        properties={"name": data.name, "description": data.description, "category": data.category},
    )
    logger.info("Concept created", name=data.name)
    return ConceptResponse(name=data.name, description=data.description, category=data.category)


@router.delete("/{name}")
@monitor_query("delete_concept")
async def delete_concept(
    name: str,
    repo: BaseRepository = Depends(get_repository),
) -> dict[str, str]:
    """Delete a concept and its relationships."""
    await repo.delete_node("Concept", name)
    logger.info("Concept deleted", name=name)
    return {"status": "deleted", "name": name}


def _query(cql: str, params: dict[str, Any]) -> Any:
    from agentverse.graph_core.models.query import Query
    return Query(cql, params)