"""Base graph node and relationship models."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GraphNode:
    """Base model for a Neo4j node."""
    labels: list[str] = field(default_factory=list)
    properties: dict[str, Any] = field(default_factory=dict)
    element_id: str | None = None


@dataclass
class GraphRelationship:
    """Base model for a Neo4j relationship."""
    type: str
    properties: dict[str, Any] = field(default_factory=dict)
    element_id: str | None = None
    start_node_id: str | None = None
    end_node_id: str | None = None