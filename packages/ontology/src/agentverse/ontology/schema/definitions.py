"""Neo4j schema definitions for ontology labels and properties."""

TAG_LABELS: dict[str, list[str]] = {
    "Agent": ["Concept", "Agent"],
    "Framework": ["Concept", "Framework"],
    "Paper": ["Concept", "Paper"],
    "Protocol": ["Concept", "Protocol"],
}

PROPERTY_DEFINITIONS: dict[str, dict[str, type]] = {
    "Agent": {"name": str, "description": str, "category": str},
    "Framework": {"name": str, "description": str, "category": str},
    "Paper": {"name": str, "doi": str, "description": str, "category": str},
    "Protocol": {"name": str, "description": str, "category": str},
}