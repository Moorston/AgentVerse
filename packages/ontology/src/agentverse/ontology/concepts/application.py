"""Application concept definition."""

from agentverse.ontology.concepts.base import Concept


class ApplicationConcept(Concept):
    """Represents an AI application or demo."""

    def __init__(self, name: str, description: str = "", tech_stack: str = "") -> None:
        super().__init__(name=name, description=description, category="application")
        self.labels = ["Concept", "Application"]
        self.properties.update({"tech_stack": tech_stack})