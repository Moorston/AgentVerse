# Ontology System Specification

## Purpose
The ontology system defines the domain model for the AI Agent knowledge graph — concepts, their properties, and relationships.

## Concept Hierarchy
```
Concept (base)
├── Agent         — AI Agent systems
├── Framework     — Development frameworks (LangGraph, CrewAI, etc.)
├── Paper         — Academic papers (DOI-keyed)
├── Protocol      — Communication protocols (MCP, A2A)
├── News          — Industry news items
├── Product       — AI products and tools
├── Company       — Companies in AI ecosystem
├── MemoryType    — Memory types (episodic, semantic, procedural, graph)
├── MemoryFramework — Memory frameworks (Mem0, Zep, LangMem)
├── Application   — AI applications and demos
├── Pattern       — Design patterns (ReAct, Reflexion, Plan-and-Execute)
└── IndustryTrend — Industry trends and directions
```

## Relationship Types (24 total)
```
PROPOSES, IMPLEMENTS, EVOLVES_TO, RELATED_TO, DEPENDS_ON, SUPPORTS,
USED_IN, REFERENCES, CITES, EXTENDS, INSPIRED_BY, AUTHORED_BY,
IMPLEMENTED_BY, ACHIEVES_SOTA, ANNOUNCED_BY, INVESTED_IN,
COLLABORATES_WITH, INTEGRATES_WITH, SUPPORTS_PATTERN,
IMPLEMENTS_MEMORY, BENCHMARKED_ON, FEATURED_IN_WEEK, TRENDING_IN, UPDATED_TO
```

## Normalizer Functions
Each concept type has a `normalize_*()` function that:
1. Takes raw dict input
2. Returns typed Concept instance
3. Sets correct labels and properties
4. Does NOT access database

## Constraints
1. All concepts MUST inherit Concept(GraphNode)
2. labels MUST include "Concept" + specific type
3. properties keys MUST be snake_case
4. New concept types MUST update schema/definitions.py
5. New relationship types MUST update RelationshipType enum

## Test Criteria
- [ ] Each concept class sets correct labels
- [ ] Each normalizer returns correct type
- [ ] Properties follow snake_case convention
- [ ] No normalizer accesses database
