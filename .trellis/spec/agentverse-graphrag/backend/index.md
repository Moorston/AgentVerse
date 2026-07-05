# GraphRAG Package Guidelines

> AgentVerse retrieval engine layer conventions

---

## Overview

`agentverse-graphrag` implements GraphRAG hybrid retrieval: vector search + graph traversal + hybrid ranking.

---

## Directory Structure

```
packages/graphrag/src/agentverse/graphrag/
├── engine.py            ← GraphRAGEngine top-level entry
├── embeddings/
│   ├── base.py          ← BaseEmbeddingModel ABC
│   └── models.py        ← OpenAIEmbeddingModel
├── retrieval/
│   ├── vector.py        ← VectorSearch (pgvector cosine similarity)
│   ├── graph.py         ← GraphSearch (Neo4j multi-hop traversal)
│   └── hybrid.py        ← HybridSearch (fusion ranking)
└── indexing/
    └── pipeline.py      ← IndexingPipeline (write to pgvector)
```

---

## Design Patterns

### Embedding models via BaseEmbeddingModel abstraction

```python
from agentverse.graphrag.embeddings.base import BaseEmbeddingModel

class OpenAIEmbeddingModel(BaseEmbeddingModel):
    async def embed(self, text: str) -> list[float]:
        """Embed text via OpenAI API."""
        ...
```

### Hybrid search fuses vector and graph results

```python
class HybridSearch:
    async def search(self, query: str, top_k: int = 10) -> list[dict]:
        vector_results = await self._vector_search.search(query, top_k)
        graph_results = await self._graph_search.search(query, top_k)
        return self._merge_and_rank(vector_results, graph_results)
```

### Neo4j and pgvector linked via node_id

```sql
CREATE TABLE node_embeddings (
    node_id TEXT NOT NULL,          -- Neo4j element_id
    embedding vector(1536) NOT NULL,
    UNIQUE(node_id)
);
```

---

## Forbidden Patterns

| Pattern | Reason |
|---------|--------|
| Direct OpenAI API call | Must use BaseEmbeddingModel subclass |
| Embedding dimension mismatch | Must match Settings.embedding_dimension |
| No result deduplication | Same node appears in vector + graph results |
| Direct JOIN between Neo4j and pgvector | Link via node_id in application layer |

---

## Common Mistakes

1. Embedding dimension hardcoded 1536 but model returns 768
2. Hybrid search concatenates without ranking → poor relevance
3. Indexing update runs synchronously → blocks API
