"""Pydantic response schemas."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Schema for health check responses."""
    status: str
    version: str


class ConceptResponse(BaseModel):
    """Schema for concept responses."""
    name: str
    description: str = ""
    category: str = ""


class ConceptDetailResponse(BaseModel):
    """Schema for concept detail with relationships."""
    name: str
    description: str = ""
    category: str = ""
    relationships: list[dict] = []


class GraphNodeResponse(BaseModel):
    """Schema for graph node in visualization."""
    id: str
    label: str
    type: str
    properties: dict = {}


class GraphEdgeResponse(BaseModel):
    """Schema for graph edge in visualization."""
    id: str
    source: str
    target: str
    type: str
    properties: dict = {}


class GraphDataResponse(BaseModel):
    """Schema for graph data (nodes + edges)."""
    nodes: list[GraphNodeResponse] = []
    edges: list[GraphEdgeResponse] = []


class SearchResponse(BaseModel):
    """Schema for search responses."""
    query: str
    results: list[dict] = []