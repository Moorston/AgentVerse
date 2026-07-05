"""Framework concept definition."""

from agentverse.ontology.concepts.base import Concept


class FrameworkConcept(Concept):
    """Represents a framework (e.g., LangGraph, CrewAI)."""

    def __init__(self, name: str, description: str = "") -> None:
        super().__init__(name=name, description=description, category="framework")
        self.labels = ["Concept", "Framework"]