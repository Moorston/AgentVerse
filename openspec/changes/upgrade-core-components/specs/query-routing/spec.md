# Spec: Query Routing and Cache for HybridSearch

## Requirements

### FR-1: Query Classification
- `QueryRouter.classify(query)` returns one of: `"semantic"`, `"structural"`, `"default"`
- Classification is rule-based (pattern matching), not LLM-based
- Classification latency must be < 1ms (no I/O)

### FR-2: Adaptive Fusion Weights
- Semantic queries: vector=0.8, graph=0.2
- Structural queries: vector=0.3, graph=0.7
- Default/ambiguous queries: vector=0.6, graph=0.4 (current behavior)
- Weights must be configurable (not hardcoded constants)

### FR-3: Result Caching
- HybridSearch caches results by `(query, top_k)` key
- Cache uses TTL (default 300 seconds, configurable)
- Cache uses LRU eviction (default 256 entries, configurable)
- Cache is invalidated when `reindex()` is called

### FR-4: Backward Compatibility
- `HybridSearch.search(query, top_k)` interface is unchanged
- `GraphRAGEngine.query()` interface is unchanged
- All existing search tests pass

## Acceptance Criteria

- [ ] "What is chain-of-thought?" → classified as `semantic` → vector-dominant
- [ ] "What frameworks depend on LangChain?" → classified as `structural` → graph-dominant
- [ ] Repeated identical query returns cached result (< 1ms on second call)
- [ ] Cache entries expire after TTL
- [ ] Default behavior (unknown queries) matches current 0.6/0.4 weights exactly
