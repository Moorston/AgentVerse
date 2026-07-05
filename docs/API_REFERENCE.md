# AgentVerse API Reference

> Base URL: `http://localhost:8000/api/v1`
>
> Interactive docs: `http://localhost:8000/docs` (Swagger UI) | `http://localhost:8000/redoc` (ReDoc)

---

## Authentication

Development mode: no authentication required.
Production mode: include `Authorization: Bearer <key>` or `X-API-Key: <key>` header.

---

## Health

### GET /health

Check system health including Neo4j, pgvector, and cache status.

```bash
curl http://localhost:8000/api/v1/health
```

Response:
```json
{
  "status": "ok",
  "version": "0.1.0",
  "services": {
    "neo4j": {"status": "ok", "nodes": 42, "relationships": 68},
    "pgvector": {"status": "ok", "embeddings": 42}
  },
  "cache": {
    "query_cache": {"size": 5, "max_size": 500, "ttl_seconds": 300},
    "concept_cache": {"size": 10, "max_size": 1000, "ttl_seconds": 600}
  }
}
```

---

## Concepts

### GET /concepts/

List all concepts with pagination and filtering.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `size` | int | 20 | Items per page (max 100) |
| `category` | string | "" | Filter by category |

```bash
curl "http://localhost:8000/api/v1/concepts/?page=1&size=10&category=reasoning"
```

### GET /concepts/{name}

Get a specific concept by name.

```bash
curl http://localhost:8000/api/v1/concepts/ReAct
```

Response:
```json
{
  "name": "ReAct",
  "description": "Reasoning + Acting paradigm",
  "category": "reasoning"
}
```

### GET /concepts/{name}/neighbors

Get N-hop neighbors of a concept.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `depth` | int | 1 | Traversal depth (1-5) |

```bash
curl "http://localhost:8000/api/v1/concepts/ReAct/neighbors?depth=2"
```

### POST /concepts/

Create a new concept.

```bash
curl -X POST http://localhost:8000/api/v1/concepts/ \
  -H "Content-Type: application/json" \
  -d '{"name": "NewConcept", "description": "A new concept", "category": "reasoning"}'
```

### DELETE /concepts/{name}

Delete a concept and its relationships.

```bash
curl -X DELETE http://localhost:8000/api/v1/concepts/NewConcept
```

### GET /concepts/{name}/timeline

Get the evolution timeline of a concept.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `direction` | string | "forward" | "forward", "backward", "both" |
| `depth` | int | 5 | Max chain length (1-10) |

```bash
curl "http://localhost:8000/api/v1/concepts/Chain-of-Thought/timeline?direction=forward"
```

### GET /concepts/{name}/connections

Get all connections of a concept.

```bash
curl http://localhost:8000/api/v1/concepts/ReAct/connections
```

---

## Search

### GET /search/

GraphRAG hybrid search. Results are cached for 5 minutes.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | string | "" | Search query (required) |
| `top_k` | int | 10 | Max results (1-100) |
| `strategy` | string | "hybrid" | "graph", "vector", "hybrid" |

```bash
curl "http://localhost:8000/api/v1/search/?q=ReAct&strategy=hybrid&top_k=5"
```

Response:
```json
{
  "query": "ReAct",
  "results": [
    {
      "name": "ReAct",
      "description": "Reasoning + Acting paradigm",
      "type": "Concept",
      "score": 1.0,
      "match": "exact"
    },
    {
      "name": "Reflexion",
      "description": "Self-reflection framework",
      "type": "Concept",
      "score": 0.8,
      "match": "neighbor"
    }
  ]
}
```

---

## Frameworks

### GET /frameworks/

List all frameworks with their capabilities.

```bash
curl "http://localhost:8000/api/v1/frameworks/?page=1&size=10"
```

### GET /frameworks/{name}

Get framework details with relationships.

```bash
curl http://localhost:8000/api/v1/frameworks/LangGraph
```

---

## Export

### GET /export/json

Export knowledge graph as JSON.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `label` | string | "" | Filter by node label |
| `limit` | int | 1000 | Max nodes (1-10000) |

```bash
curl "http://localhost:8000/api/v1/export/json?label=Concept&limit=100"
```

### GET /export/csv

Export nodes as CSV file download.

```bash
curl -o export.csv "http://localhost:8000/api/v1/export/csv?label=Framework"
```

---

## Batch Operations

### POST /batch/concepts

Batch create concepts.

```bash
curl -X POST http://localhost:8000/api/v1/batch/concepts \
  -H "Content-Type: application/json" \
  -d '{
    "concepts": [
      {"name": "Concept1", "description": "First concept", "category": "reasoning"},
      {"name": "Concept2", "description": "Second concept", "category": "planning"}
    ]
  }'
```

Response:
```json
{
  "created": 2,
  "errors": 0,
  "details": []
}
```

### POST /batch/relationships

Batch create relationships.

```bash
curl -X POST http://localhost:8000/api/v1/batch/relationships \
  -H "Content-Type: application/json" \
  -d '{
    "relationships": [
      {"source": "Concept1", "target": "Concept2", "type": "EVOLVES_TO"},
      {"source": "Concept2", "target": "ReAct", "type": "RELATED_TO"}
    ]
  }'
```

### DELETE /batch/concepts

Batch delete concepts by name.

```bash
curl -X DELETE "http://localhost:8000/api/v1/batch/concepts?names=Concept1&names=Concept2"
```

---

## Rate Limiting

| Limit | Value |
|-------|-------|
| Requests per minute | 60 |
| Requests per hour | 1000 |

Rate limit headers:
```
X-RateLimit-Limit-Minute: 60
X-RateLimit-Remaining-Minute: 59
X-RateLimit-Limit-Hour: 1000
X-RateLimit-Remaining-Hour: 999
X-Response-Time: 42.15ms
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": "Not Found",
  "detail": "Concept 'Unknown' not found",
  "status_code": 404
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (missing API key) |
| 404 | Not Found |
| 429 | Too Many Requests (rate limited) |
| 500 | Internal Server Error |
| 503 | Service Unavailable (database down) |
