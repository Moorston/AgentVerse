# Spec: LLM Extraction via PydanticAI

## Requirements

### FR-1: Typed Extraction Results
- Each extractor must return a strongly-typed Pydantic model (not `dict`)
- `PaperExtractor` → `PaperResult`
- `ConceptExtractor` → `ConceptResult`
- `RelationshipExtractor` → `RelationshipResult`
- Invalid or incomplete LLM output must trigger a retry, not a silent fallback

### FR-2: Automatic Retry
- LLM calls must retry up to 3 times on transient failures (timeout, rate limit, parse error)
- Retries must use exponential backoff (handled by PydanticAI)
- After max retries, raise `ExtractionError` (subclass of `AgentVerseError`)

### FR-3: Provider Abstraction
- `LLMClient` must support OpenAI and Anthropic providers via a single `get_agent()` method
- Provider selection is driven by `Settings.openai_api_key` / `Settings.anthropic_api_key`
- No provider-specific code in extractor classes

### FR-4: Backward Compatibility
- `ExtractionResult` remains the public return type of all extractors
- `ExtractionPipeline` interface is unchanged
- Worker task functions (`run_extract`) continue to work without modification

## Acceptance Criteria

- [ ] `PaperExtractor.extract()` returns `ExtractionResult` containing typed `PaperResult` data
- [ ] A malformed LLM JSON response triggers retry (up to 3 times) before raising error
- [ ] Switching provider requires only changing env vars, no code changes
- [ ] All existing extractor tests pass with mocked Agent
