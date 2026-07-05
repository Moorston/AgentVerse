"""AI Agent concept definition."""

from agentverse.ontology.concepts.base import Concept


class AgentConcept(Concept):
    """Represents an AI Agent in the knowledge graph."""

    def __init__(self, name: str, description: str = "") -> None:
        super().__init__(name=name, description=description, category="agent")
        self.labels = ["Concept", "Agent"]