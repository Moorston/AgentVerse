"""Pattern concept definition."""

from agentverse.ontology.concepts.base import Concept


class PatternConcept(Concept):
    """Represents an AI Agent design pattern (ReAct, Reflexion, Plan-and-Execute)."""

    def __init__(self, name: str, description: str = "") -> None:
        super().__init__(name=name, description=description, category="pattern")
        self.labels = ["Concept", "Pattern"]