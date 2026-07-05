# Extractor Package Guidelines

> AgentVerse LLM information extraction layer conventions

---

## Overview

`agentverse-extractor` uses LLMs to extract structured entities and relationships from unstructured text.

---

## Directory Structure

```
packages/extractor/src/agentverse/extractor/
├── base.py              ← BaseExtractor ABC + ExtractionResult
├── llm/
│   ├── client.py        ← LLMClient (OpenAI / Anthropic dual channel)
│   └── prompts.py       ← Extraction prompt templates
├── extractors/
│   ├── paper.py         ← PaperExtractor
│   ├── concept.py       ← ConceptExtractor
│   └── relationship.py  ← RelationshipExtractor
└── pipeline.py          ← ExtractionPipeline
```

---

## Design Patterns

### All extractors inherit BaseExtractor

```python
from agentverse.extractor.base import BaseExtractor, ExtractionResult

class PaperExtractor(BaseExtractor):
    async def extract(self, text: str, **kwargs) -> ExtractionResult:
        """Extract paper metadata from text."""
        ...
```

### LLM calls must go through LLMClient

```python
from agentverse.extractor.llm.client import LLMClient

client = LLMClient(provider="openai", api_key=settings.openai_api_key)
result = await client.complete(prompt, response_format={"type": "json_object"})
```

### Output must use JSON Schema format

```python
response_format = {
    "type": "json_object",
    "schema": {
        "type": "object",
        "properties": {
            "concepts": {"type": "array"},
            "relationships": {"type": "array"}
        }
    }
}
```

---

## Forbidden Patterns

| Pattern | Reason |
|---------|--------|
| Direct OpenAI/Anthropic client | Must use LLMClient |
| Direct database writes | Only return ExtractionResult |
| Unnormalized concept names | "ReAct" vs "react" → duplicate nodes |
| Relationship types outside enum | Must use RelationshipType values |
| Skip retry logic | Use `@retry` from shared/utils/retry.py |

---

## Common Mistakes

1. LLM returns non-JSON → must use response_format constraint
2. Concept "ReAct" becomes "react" → duplicate nodes
3. No timeout on single paper processing → must set timeout=10s
