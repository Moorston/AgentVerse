"""Neo4j schema definitions for ontology labels and properties."""

TAG_LABELS: dict[str, list[str]] = {
    "Agent": ["Concept", "Agent"],
    "Framework": ["Concept", "Framework"],
    "Paper": ["Concept", "Paper"],
    "Protocol": ["Concept", "Protocol"],
    "News": ["Concept", "News"],
    "Product": ["Concept", "Product"],
    "Company": ["Concept", "Company"],
    "MemoryType": ["Concept", "MemoryType"],
    "MemoryFramework": ["Concept", "MemoryFramework"],
    "Application": ["Concept", "Application"],
    "Pattern": ["Concept", "Pattern"],
    "IndustryTrend": ["Concept", "IndustryTrend"],
}

PROPERTY_DEFINITIONS: dict[str, dict[str, type]] = {
    "Agent": {"name": str, "description": str, "category": str},
    "Framework": {"name": str, "description": str, "category": str},
    "Paper": {"name": str, "doi": str, "description": str, "category": str},
    "Protocol": {"name": str, "description": str, "category": str},
    "News": {"name": str, "description": str, "category": str, "url": str, "source": str},
    "Product": {"name": str, "description": str, "category": str, "company": str},
    "Company": {"name": str, "description": str, "category": str},
    "MemoryType": {"name": str, "description": str, "category": str, "memory_category": str},
    "MemoryFramework": {"name": str, "description": str, "category": str, "github_url": str},
    "Application": {"name": str, "description": str, "category": str, "tech_stack": str},
    "Pattern": {"name": str, "description": str, "category": str},
    "IndustryTrend": {"name": str, "description": str, "category": str, "direction": str, "strength": str},
}