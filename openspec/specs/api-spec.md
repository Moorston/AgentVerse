# API System Specification

## Purpose
FastAPI REST API providing knowledge graph CRUD, GraphRAG search, and framework ecosystem queries.

## Endpoints
```
GET    /api/v1/health                       — service health
GET    /api/v1/concepts/                    — list concepts (paginated)
GET    /api/v1/concepts/{name}              — concept detail
GET    /api/v1/concepts/{name}/neighbors    — N-hop subgraph
POST   /api/v1/concepts/                    — create concept
DELETE /api/v1/concepts/{name}              — delete concept
GET    /api/v1/concepts/{name}/timeline     — evolution chain
GET    /api/v1/concepts/{name}/connections  — all connections
GET    /api/v1/search/                      — GraphRAG search
GET    /api/v1/frameworks/                  — framework list
GET    /api/v1/frameworks/{name}            — framework detail
```

## Constraints
1. All endpoints MUST return Pydantic models (never raw dict)
2. All endpoints MUST be async def
3. Database connections via Depends() injection
4. Pagination: ?page=1&size=20 (max size=100)
5. Error responses: {"error", "detail", "status_code"}
6. Rate limiting: 60 req/min, 1000 req/hour
7. CORS: allow all origins (development)

## Middleware Stack
```
CORS → Rate Limiter → Request Logger → Error Handler
```

## Response Headers
```
X-Response-Time: 42.15ms
X-RateLimit-Limit-Minute: 60
X-RateLimit-Remaining-Minute: 59
```

## Test Criteria
- [ ] /health returns 200 with status and version
- [ ] /concepts returns paginated list
- [ ] /search supports graph, vector, hybrid strategies
- [ ] Rate limiting returns 429 on excess
- [ ] Error handler converts exceptions to JSON
