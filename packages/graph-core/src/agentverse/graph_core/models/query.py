"""Query builder abstractions."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Query:
    """Represents a Cypher query with parameters."""
    statement: str
    parameters: dict[str, Any] = field(default_factory=dict)