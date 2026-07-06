"""Data export endpoint — export knowledge graph as JSON or CSV."""

import csv
import io
import json
from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from agentverse.api.core.dependencies import get_repository
from agentverse.graph_core.repository.base import BaseRepository
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/json")
async def export_json(
    label: str = Query("", description="Filter by node label"),
    limit: int = Query(1000, ge=1, le=10000),
    repo: BaseRepository = Depends(get_repository),
) -> dict[str, Any]:
    """Export knowledge graph as JSON.

    Returns nodes and edges in a format suitable for visualization tools.
    """
    # Fetch nodes
    if label:
        nodes = await repo.execute_raw(
            f"MATCH (n:{label}) RETURN n LIMIT $limit",
            {"limit": limit},
        )
    else:
        nodes = await repo.execute_raw(
            "MATCH (n) RETURN n LIMIT $limit",
            {"limit": limit},
        )

    # Fetch relationships
    rels = await repo.execute_raw(
        "MATCH (a)-[r]->(b) RETURN a.name AS source, b.name AS target, type(r) AS rel_type LIMIT $limit",
        {"limit": limit},
    )

    return {
        "nodes": [
            {
                "id": n.get("n", {}).get("name", ""),
                "labels": n.get("n", {}).get("labels", []),
                "properties": dict(n.get("n", {})),
            }
            for n in nodes
        ],
        "edges": [
            {
                "source": r["source"],
                "target": r["target"],
                "type": r["rel_type"],
            }
            for r in rels
        ],
        "metadata": {
            "node_count": len(nodes),
            "edge_count": len(rels),
        },
    }


@router.get("/csv")
async def export_csv(
    label: str = Query("", description="Filter by node label"),
    limit: int = Query(1000, ge=1, le=10000),
    repo: BaseRepository = Depends(get_repository),
) -> StreamingResponse:
    """Export knowledge graph nodes as CSV."""
    if label:
        nodes = await repo.execute_raw(
            f"MATCH (n:{label}) RETURN n.name AS name, n.description AS description, labels(n) AS labels SKIP 0 LIMIT $limit",
            {"limit": limit},
        )
    else:
        nodes = await repo.execute_raw(
            "MATCH (n) RETURN n.name AS name, n.description AS description, labels(n) AS labels SKIP 0 LIMIT $limit",
            {"limit": limit},
        )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["name", "description", "labels"])
    for n in nodes:
        writer.writerow([
            n.get("name", ""),
            n.get("description", ""),
            "|".join(n.get("labels", [])),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=agentverse_export.csv"},
    )