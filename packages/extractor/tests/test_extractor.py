"""Tests for extractor base and prompts."""

from agentverse.extractor.base import ExtractionResult, BaseExtractor
from agentverse.extractor.llm.prompts import (
    PAPER_EXTRACTION_PROMPT,
    CONCEPT_EXTRACTION_PROMPT,
    RELATIONSHIP_EXTRACTION_PROMPT,
)


def test_extraction_result_defaults():
    """Test ExtractionResult default values."""
    result = ExtractionResult(source="test")
    assert result.source == "test"
    assert result.entities == []
    assert result.relationships == []


def test_extraction_result_with_data():
    """Test ExtractionResult with data."""
    result = ExtractionResult(
        source="test",
        entities=[{"type": "concept", "name": "ReAct"}],
        relationships=[{"source": "ReAct", "target": "Tool Calling", "type": "RELATED_TO"}],
    )
    assert len(result.entities) == 1
    assert len(result.relationships) == 1


def test_paper_extraction_prompt():
    """Test paper extraction prompt template."""
    prompt = PAPER_EXTRACTION_PROMPT.format(text="Test paper text")
    assert "Test paper text" in prompt
    assert "Title" in prompt


def test_concept_extraction_prompt():
    """Test concept extraction prompt template."""
    prompt = CONCEPT_EXTRACTION_PROMPT.format(text="Test text")
    assert "Test text" in prompt
    assert "concept" in prompt.lower()


def test_relationship_extraction_prompt():
    """Test relationship extraction prompt template."""
    prompt = RELATIONSHIP_EXTRACTION_PROMPT.format(text="Test text")
    assert "Test text" in prompt
    assert "relationship" in prompt.lower()