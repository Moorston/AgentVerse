# Extractor System Specification

## Purpose
The extractor system uses LLMs to extract structured entities and relationships from unstructured text.

## Architecture
```
LLMClient (OpenAI-compatible APIs + Anthropic)
├── PaperExtractor       — paper metadata extraction
├── ConceptExtractor     — concept identification
└── RelationshipExtractor — relationship extraction
```

## Data Flow
```
Crawled Text → LLMClient.complete_json() → ExtractionResult → Pipeline
```

## Constraints
1. All extractors MUST inherit BaseExtractor
2. LLM calls MUST go through LLMClient (not direct API calls)
3. Output MUST use JSON Schema format (response_format)
4. Concept names MUST be normalized (PascalCase, no trailing spaces)
5. Relationship types MUST be within RelationshipType enum
6. Single paper timeout: 10s (GPT-4o), 30s (Claude)
7. LLMClient SHALL read api_key, base_url, and model from Settings() when not provided explicitly
8. LLMClient SHALL accept `base_url` parameter for OpenAI-compatible APIs (Sensenova, DeepSeek, Moonshot, etc.)
9. Prompts SHALL enforce PascalCase naming with negative examples (no "LLMs", "AI", "models", "data")
10. RelationshipExtractor SHALL enforce source=target direction: source=acting method, target=affected entity
11. PaperExtractor SHALL assign category to each concept using the same enum as ConceptExtractor

## ExtractionResult Schema
```python
@dataclass
class ExtractionResult:
    source: str              # "paper" | "concept" | "relationship"
    entities: list[dict]     # [{type, name, description, category}]
    relationships: list[dict] # [{source, target, type, evidence}]
```

## Prompt Templates
- PAPER_EXTRACTION_PROMPT — extracts title, authors, abstract, concepts, frameworks
- CONCEPT_EXTRACTION_PROMPT — extracts named concepts with categories
- RELATIONSHIP_EXTRACTION_PROMPT — extracts typed relationships

## Test Criteria
- [ ] PaperExtractor extracts title, authors, concepts from abstract
- [ ] ConceptExtractor normalizes names correctly
- [ ] RelationshipExtractor constrains to valid relationship types
- [ ] LLMClient handles both OpenAI and Anthropic
- [ ] Retry logic works on transient failures
