"""Pydantic request schemas."""

from pydantic import BaseModel


class ConceptCreate(BaseModel):
    """Schema for creating a new concept."""
    name: str
    description: str = ""
    category: str = ""

class SearchQuery(BaseModel):
    """Schema for search requests."""
    q: str
    top_k: int = 10