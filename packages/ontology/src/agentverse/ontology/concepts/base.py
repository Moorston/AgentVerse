"""Base concept definitions."""

from dataclasses import dataclass, field
from typing import Any

from agentverse.graph_core.models.node import GraphNode


@dataclass
class Concept(GraphNode):
    """A concept in the AI Agent ecosystem."""
    name: str = ""
    description: str = ""
    category: str = ""

    def __post_init__(self) -> None:
        self.labels = ["Concept"]
        self.properties = {
            "name": self.name,
            "description": self.description,
            "category": self.category,
        }