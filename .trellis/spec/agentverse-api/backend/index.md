# API Package Guidelines

> AgentVerse REST API layer conventions

---

## Overview

`agentverse-api` is the FastAPI backend providing knowledge graph queries and GraphRAG search.

---

## Directory Structure

```
apps/api/src/agentverse/api/
├── main.py              ← create_app() factory
├── core/
│   ├── config.py        ← APISettings(Settings)
│   ├── dependencies.py  ← FastAPI Depends()
│   ├── events.py        ← lifespan context manager
│   └── middleware.py    ← CORS / Logging / Error
├── api/v1/
│   ├── router.py        ← api_v1_router aggregator
│   ├── health.py        ← GET /health
│   ├── concepts.py      ← /concepts CRUD
│   └── search.py        ← /search GraphRAG
├── db/
│   ├── neo4j.py         ← Neo4j connection pool
│   └── postgres.py      ← PostgreSQL connection pool
└── models/
    ├── request.py       ← Pydantic request models
    └── response.py      ← Pydantic response models
```

---

## API Design Rules

### All endpoints return Pydantic models (never raw dict)

```python
from agentverse.api.models.response import ConceptResponse

@router.get("/concepts/{name}")
async def get_concept(name: str) -> ConceptResponse:
    ...
```

### Unified pagination

```python
@router.get("/concepts")
async def list_concepts(page: int = 1, size: int = 20) -> list[ConceptResponse]:
    ...
```

### Unified error handling (in middleware.py)

```
AgentVerseError  → 400 Bad Request
NotFoundError    → 404 Not Found
DatabaseError    → 503 Service Unavailable
Exception        → 500 Internal Server Error
```

### Dependency injection via Depends()

```python
from fastapi import Depends
from agentverse.api.core.dependencies import get_graph_client

@router.get("/concepts/{name}")
async def get_concept(name: str, client = Depends(get_graph_client)):
    ...
```

---

## Forbidden Patterns

| Pattern | Reason |
|---------|--------|
| Return raw `dict` | Must use Pydantic response model |
| Create DB connection in endpoint | Use `Depends()` injection |
| Write Cypher in endpoint | Use Repository pattern |
| Non-async endpoint functions | Blocks event loop |
| Hardcode CORS origins | Configure via Settings |

---

## Common Mistakes

1. Forgetting `async def` → blocks event loop
2. Missing Pydantic defaults → 422 Unprocessable Entity
3. CORS middleware order wrong → must be registered before routes
