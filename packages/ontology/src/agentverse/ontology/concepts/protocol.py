"""Protocol concept definition (MCP, A2A)."""

from agentverse.ontology.concepts.base import Concept


class ProtocolConcept(Concept):
    """Represents a protocol (e.g., MCP, A2A)."""

    def __init__(self, name: str, description: str = "") -> None:
        super().__init__(name=name, description=description, category="protocol")
        self.labels = ["Concept", "Protocol"]