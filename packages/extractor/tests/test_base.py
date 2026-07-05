"""Tests for extractor base models."""

from agentverse.extractor.base import ExtractionResult, BaseExtractor


def test_extraction_result_defaults():
    """ExtractionResult should have empty defaults."""
    result = ExtractionResult(source="test")
    assert result.source == "test"
    assert result.entities == []
    assert result.relationships == []


def test_extraction_result_with_data():
    """ExtractionResult should store entities and relationships."""
    result = ExtractionResult(
        source="paper",
        entities=[{"name": "ReAct", "type": "Concept"}],
        relationships=[{"source": "ReAct", "target": "Tool", "type": "RELATED_TO"}],
    )
    assert len(result.entities) == 1
    assert len(result.relationships) == 1


def test_extraction_result_from_dict():
    """ExtractionResult should work as dataclass."""
    result = ExtractionResult(source="test", entities=[], relationships=[])
    assert result.source == "test"
