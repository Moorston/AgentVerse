"""Industry trend concept definition."""

from agentverse.ontology.concepts.base import Concept


class IndustryTrendConcept(Concept):
    """Represents an industry trend or direction."""

    def __init__(self, name: str, description: str = "", direction: str = "", strength: str = "") -> None:
        super().__init__(name=name, description=description, category="industry_trend")
        self.labels = ["Concept", "IndustryTrend"]
        self.properties.update({"direction": direction, "strength": strength})