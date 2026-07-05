"""Memory framework concept definition."""

from agentverse.ontology.concepts.base import Concept


class MemoryFrameworkConcept(Concept):
    """Represents a memory framework (Mem0, Zep, LangMem, Letta, Cognee)."""

    def __init__(self, name: str, description: str = "", github_url: str = "") -> None:
        super().__init__(name=name, description=description, category="memory_framework")
        self.labels = ["Concept", "MemoryFramework"]
        self.properties.update({"github_url": github_url})