# GraphRAG System Specification

## Purpose
The GraphRAG engine combines vector similarity search (pgvector) with knowledge graph traversal (Neo4j) for high-quality retrieval.

## Architecture
```
GraphRAGEngine
├── OpenAIEmbeddingModel — text-embedding-3-small (1536d)
├── VectorSearch         — pgvector cosine similarity
├── GraphSearch          — Neo4j multi-hop traversal
├── HybridSearch         — fusion ranking (0.6*vector + 0.4*graph)
└── IndexingPipeline     — batch embedding + pgvector write
```

## Data Flow
```
Query Text → HybridSearch.search()
  ├── VectorSearch: embed(query) → pgvector cosine → ranked results
  └── GraphSearch: exact match → fuzzy match → multi-hop → ranked results
  → Fusion ranking → Top-K results
```

## Search Strategies
| Strategy | Description | Requires |
|----------|-------------|----------|
| graph | Multi-hop Neo4j traversal | Neo4j only |
| vector | pgvector cosine similarity | Neo4j + pgvector |
| hybrid | Combined with fusion ranking | Neo4j + pgvector |

## Fusion Ranking Formula
```
combined_score = 0.6 * vector_score + 0.4 * graph_score
```

## Constraints
1. Embedding dimension MUST match Settings.embedding_dimension (default 1536)
2. VectorSearch and GraphSearch MUST be independently functional
3. HybridSearch MUST deduplicate results by node name
4. IndexingPipeline MUST use batch embedding for efficiency
5. Neo4j and pgvector linked via node_id (no direct JOIN)
6. VectorSearch SHALL accept a store instance via constructor injection — no cross-package imports from `agentverse.api.*`
7. GraphRAGEngine.initialize() SHALL pass the created PgVectorStore instance to VectorSearch and IndexingPipeline
8. The `graphrag.retrieval` package SHALL export VectorSearch, GraphSearch, HybridSearch, and PgVectorStore

## Test Criteria
- [ ] VectorSearch returns cosine-similarity-ranked results
- [ ] GraphSearch performs exact → fuzzy → multi-hop search
- [ ] HybridSearch merges and deduplicates correctly
- [ ] IndexingPipeline batches embeddings efficiently
- [ ] Engine gracefully handles missing pgvector (falls back to graph-only)
