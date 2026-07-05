# AgentVerse — Architecture

## Overview

```
Source Crawlers ──→ LLM Extractor ──→ Ontology Normalizer ──→ Neo4j Knowledge Graph
                                                                      │
                                                                      ▼
                                                               GraphRAG Engine
                                                                      │
                                                                      ▼
                                                               API Gateway
                                                                      │
                                                                      ▼
                                                               Next.js UI
```

## Package Dependency DAG

```
shared → graph-core → [ontology, graphrag] → [crawler → extractor] → [api, worker]
```

## Key Decisions

- **Namespace packages**: All Python under `agentverse.*`, `src/` layout
- **Build system**: uvw + Hatchling
- **Async-first**: FastAPI, Neo4j async driver
- **Worker**: Simple polling loop (upgradeable to Celery/ARQ later)
- **Databases**: Neo4j (graph) + PostgreSQL+pgvector (vectors)