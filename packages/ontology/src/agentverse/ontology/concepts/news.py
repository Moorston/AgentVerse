"""News concept definition."""

from agentverse.ontology.concepts.base import Concept


class NewsConcept(Concept):
    """Represents an industry news item."""

    def __init__(self, name: str, url: str = "", source: str = "", summary: str = "") -> None:
        super().__init__(name=name, description=summary, category="news")
        self.labels = ["Concept", "News"]
        self.properties.update({"url": url, "source": source})