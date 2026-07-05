"""Company concept definition."""

from agentverse.ontology.concepts.base import Concept


class CompanyConcept(Concept):
    """Represents a company in the AI ecosystem."""

    def __init__(self, name: str, description: str = "") -> None:
        super().__init__(name=name, description=description, category="company")
        self.labels = ["Concept", "Company"]