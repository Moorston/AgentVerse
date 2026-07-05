"""Paper concept definition."""

from agentverse.ontology.concepts.base import Concept


class PaperConcept(Concept):
    """Represents a research paper."""

    def __init__(self, name: str, doi: str = "", description: str = "") -> None:
        super().__init__(name=name, description=description, category="paper")
        self.labels = ["Concept", "Paper"]
        self.properties["doi"] = doi