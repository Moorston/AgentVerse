"""Memory type concept definition."""

from agentverse.ontology.concepts.base import Concept


class MemoryTypeConcept(Concept):
    """Represents a type of agent memory (episodic, semantic, procedural, graph)."""

    def __init__(self, name: str, description: str = "", memory_category: str = "") -> None:
        super().__init__(name=name, description=description, category="memory_type")
        self.labels = ["Concept", "MemoryType"]
        self.properties.update({"memory_category": memory_category})