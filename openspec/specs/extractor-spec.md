# Extractor System Specification

## Purpose
The extractor system uses LLMs to extract structured entities and relationships from unstructured text.

## Architecture
```
LLMClient (OpenAI + Anthropic)
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
