"""Tests for extractor pipeline."""

import pytest

from agentverse.extractor.base import BaseExtractor, ExtractionResult
from agentverse.extractor.pipeline import ExtractionPipeline
from agentverse.extractor.types import ExtractionRequest


class MockExtractor(BaseExtractor):
    """Mock extractor for testing."""

    def __init__(self, entities: list[dict] | None = None):
        self._entities = entities or []

    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        return ExtractionResult(source="mock", entities=self._entities)


@pytest.mark.asyncio
async def test_pipeline_empty():
    """Empty pipeline should return empty results."""
    pipeline = ExtractionPipeline()
    results = await pipeline.run_all({"text": "test text"})
    assert results == []


@pytest.mark.asyncio
async def test_pipeline_single_extractor():
    """Pipeline should run registered extractor."""
    pipeline = ExtractionPipeline()
    pipeline.register(MockExtractor([{"name": "ReAct"}]))
    results = await pipeline.run_all({"text": "some paper text"})
    assert len(results) == 1
    assert results[0].entities == [{"name": "ReAct"}]


@pytest.mark.asyncio
async def test_pipeline_multiple_extractors():
    """Pipeline should run all registered extractors."""
    pipeline = ExtractionPipeline()
    pipeline.register(MockExtractor([{"name": "A"}]))
    pipeline.register(MockExtractor([{"name": "B"}]))
    results = await pipeline.run_all({"text": "text"})
    assert len(results) == 2
