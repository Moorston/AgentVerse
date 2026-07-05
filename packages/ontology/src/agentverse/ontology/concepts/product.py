"""Product concept definition."""

from agentverse.ontology.concepts.base import Concept


class ProductConcept(Concept):
    """Represents an AI product or tool."""

    def __init__(self, name: str, company: str = "", description: str = "") -> None:
        super().__init__(name=name, description=description, category="product")
        self.labels = ["Concept", "Product"]
        self.properties.update({"company": company})