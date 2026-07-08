# Tasks: Upgrade Core Components

## Phase 1: PydanticAI for LLM Extraction

- [ ] 1.1 Add `pydantic-ai>=0.2,<1.0` to `packages/extractor/pyproject.toml`
- [ ] 1.2 Add Pydantic result types to `packages/extractor/types.py` (PaperResult, ConceptResult, RelationshipResult)
- [ ] 1.3 Rewrite `packages/extractor/llm/client.py` — LLMClient becomes Agent factory
- [ ] 1.4 Update `packages/extractor/extractors/paper.py` to use `Agent[PaperResult]`
- [ ] 1.5 Update `packages/extractor/extractors/concept.py` to use `Agent[ConceptResult]`
- [ ] 1.6 Update `packages/extractor/extractors/relationship.py` to use `Agent[RelationshipResult]`
- [ ] 1.7 Update extractor tests to mock PydanticAI Agent
- [ ] 1.8 Verify: `uv run pytest packages/extractor/tests/`

## Phase 2: TaskIQ for Worker Orchestration

- [ ] 2.1 Add `taskiq>=0.11,<1.0` to `apps/worker/pyproject.toml`
- [ ] 2.2 Create `apps/worker/src/agentverse/worker/broker.py` with MemoryBroker + event hooks
- [ ] 2.3 Rewrite `apps/worker/src/agentverse/worker/tasks/crawl.py` as `@broker.task`
- [ ] 2.4 Rewrite `apps/worker/src/agentverse/worker/tasks/extract.py` as `@broker.task`
- [ ] 2.5 Rewrite `apps/worker/src/agentverse/worker/tasks/index.py` as `@broker.task`
- [ ] 2.6 Add task chaining: crawl → extract → index via `.kiq()`
- [ ] 2.7 Rewrite `apps/worker/src/agentverse/worker/main.py` to start TaskIQ worker
- [ ] 2.8 Delete `apps/worker/src/agentverse/worker/scheduler.py`
- [ ] 2.9 Update worker tests
- [ ] 2.10 Verify: `uv run pytest apps/worker/tests/`

## Phase 3: Query Router + Cache for HybridSearch

- [ ] 3.1 Add `cachetools>=5.0,<6.0` to `packages/graphrag/pyproject.toml`
- [ ] 3.2 Create `packages/graphrag/retrieval/router.py` with QueryRouter (rule-based classification)
- [ ] 3.3 Modify `packages/graphrag/retrieval/hybrid.py` — integrate QueryRouter and TTLCache
- [ ] 3.4 Add unit tests for QueryRouter classification
- [ ] 3.5 Add tests for cache hit/miss/TTL in HybridSearch
- [ ] 3.6 Verify: `uv run pytest packages/graphrag/tests/`

## Phase 4: Integration Verification

- [ ] 4.1 Run full test suite: `uv run pytest` across all packages
- [ ] 4.2 Verify DAG dependency check: no new cross-package imports
- [ ] 4.3 Update `docs/ARCHITECTURE_DESIGN.md` sections 5.2, 5.4, 6.2 to reflect changes
