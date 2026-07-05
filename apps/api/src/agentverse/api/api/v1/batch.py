"""Batch operations endpoint — bulk create/delete/import."""

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from agentverse.api.core.dependencies import get_repository
from agentverse.graph_core.repository.base import BaseRepository
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class BatchCreateRequest(BaseModel):
    """Request model for batch concept creation."""
    concepts: list[dict[str, Any]]


class BatchRelationshipRequest(BaseModel):
    """Request model for batch relationship creation."""
    relationships: list[dict[str, Any]]


class BatchResponse(BaseModel):
    """Response model for batch operations."""
    created: int
    errors: int
    details: list[str] = []


@router.post("/concepts", response_model=BatchResponse)
async def batch_create_concepts(
    request: BatchCreateRequest,
    repo: BaseRepository = Depends(get_repository),
) -> BatchResponse:
    """Batch create concepts.

    Each concept must have at least a 'name' field.
    Optional: 'description', 'category'.
    """
    created = 0
    errors = 0
    details: list[str] = []

    for concept in request.concepts:
        name = concept.get("name", "")
        if not name:
            errors += 1
            details.append(f"Skipped: missing name")
            continue

        try:
            await repo.create_node(
                labels=["Concept"],
                properties={
                    "name": name,
                    "description": concept.get("description", ""),
                    "category": concept.get("category", ""),
                },
            )
            created += 1
        except Exception as exc:
            errors += 1
            details.append(f"Error creating '{name}': {exc}")

    logger.info("Batch create complete", created=created, errors=errors)
    return BatchResponse(created=created, errors=errors, details=details[:20])


@router.post("/relationships", response_model=BatchResponse)
async def batch_create_relationships(
    request: BatchRelationshipRequest,
    repo: BaseRepository = Depends(get_repository),
) -> BatchResponse:
    """Batch create relationships.

    Each relationship must have: source, target, type.
    """
    created = 0
    errors = 0
    details: list[str] = []

    for rel in request.relationships:
        source = rel.get("source", "")
        target = rel.get("target", "")
        rel_type = rel.get("type", "RELATED_TO")

        if not source or not target:
            errors += 1
            details.append("Skipped: missing source or target")
            continue

        try:
            await repo.create_relationship(
                "Concept", source, "Concept", target, rel_type,
            )
            created += 1
        except Exception as exc:
            errors += 1
            details.append(f"Error creating '{source}' -> '{target}': {exc}")

    logger.info("Batch relationships complete", created=created, errors=errors)
    return BatchResponse(created=created, errors=errors, details=details[:20])


@router.delete("/concepts")
async def batch_delete_concepts(
    names: list[str],
    repo: BaseRepository = Depends(get_repository),
) -> BatchResponse:
    """Batch delete concepts by name."""
    deleted = 0
    errors = 0
    details: list[str] = []

    for name in names:
        try:
            await repo.delete_node("Concept", name)
            deleted += 1
        except Exception as exc:
            errors += 1
            details.append(f"Error deleting '{name}': {exc}")

    logger.info("Batch delete complete", deleted=deleted, errors=errors)
    return BatchResponse(created=deleted, errors=errors, details=details[:20])