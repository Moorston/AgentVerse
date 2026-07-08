"""Tests for extractor implementations.

Tests at the public seam: extract() -> ExtractionResult.
PydanticAI Agent is mocked via constructor injection; behavior is verified through return values.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from agentverse.extractor.extractors.paper import PaperExtractor
from agentverse.extractor.extractors.concept import ConceptExtractor
from agentverse.extractor.extractors.relationship import RelationshipExtractor
from agentverse.extractor.types import (
    PaperResult,
    ConceptResult,
    RelationshipResult,
    ExtractedConcept,
    ExtractedRelationship,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def mock_agent(result_data):
    """Create a mock PydanticAI Agent that returns fixed typed data.

    Args:
        result_data: A Pydantic model instance (PaperResult, ConceptResult, etc.)

    Returns:
        Mock Agent with .run() returning an object whose .data is result_data.
    """
    run_result = MagicMock()
    run_result.data = result_data
    agent = MagicMock()
    agent.run = AsyncMock(return_value=run_result)
    return agent


def mock_agent_failure(exc: Exception = Exception("API timeout")):
    """Create a mock Agent that raises on .run()."""
    agent = MagicMock()
    agent.run = AsyncMock(side_effect=exc)
    return agent


# ---------------------------------------------------------------------------
# PaperExtractor
# ---------------------------------------------------------------------------


SAMPLE_PAPER_RESULT = PaperResult(
    title="ReAct: Synergizing Reasoning and Acting in Language Models",
    authors=["Shunyu Yao", "Jeffrey Zhao"],
    abstract="LLMs can generate reasoning traces and task actions.",
    concepts=[
        ExtractedConcept(name="ReAct", category="reasoning"),
        ExtractedConcept(name="ChainOfThought", category="reasoning"),
        ExtractedConcept(name="ToolCalling", category="tool_use"),
    ],
    frameworks=["LangChain"],
    contribution_type="method",
)


class TestPaperExtractor:
    """Tests for PaperExtractor at the extract() seam."""

    @pytest.mark.asyncio
    async def test_extract_returns_paper_entity(self):
        """Paper metadata is returned as the first entity with type='paper'."""
        extractor = PaperExtractor(agent=mock_agent(SAMPLE_PAPER_RESULT))
        result = await extractor.extract({"text": "ReAct paper content..."})

        assert result.source == "paper"
        paper_entities = [e for e in result.entities if e["type"] == "paper"]
        assert len(paper_entities) == 1
        assert paper_entities[0]["name"] == "ReAct: Synergizing Reasoning and Acting in Language Models"

    @pytest.mark.asyncio
    async def test_extract_returns_concept_entities(self):
        """Each concept from LLM response becomes a separate entity."""
        extractor = PaperExtractor(agent=mock_agent(SAMPLE_PAPER_RESULT))
        result = await extractor.extract({"text": "..."})

        concept_entities = [e for e in result.entities if e["type"] == "concept"]
        assert len(concept_entities) == 3
        names = {e["name"] for e in concept_entities}
        assert names == {"ReAct", "ChainOfThought", "ToolCalling"}

    @pytest.mark.asyncio
    async def test_extract_returns_framework_entities(self):
        """Each framework from LLM response becomes a separate entity."""
        extractor = PaperExtractor(agent=mock_agent(SAMPLE_PAPER_RESULT))
        result = await extractor.extract({"text": "..."})

        fw_entities = [e for e in result.entities if e["type"] == "framework"]
        assert len(fw_entities) == 1
        assert fw_entities[0]["name"] == "LangChain"

    @pytest.mark.asyncio
    async def test_extract_creates_proposes_relationships(self):
        """Each concept gets a PROPOSES relationship from the paper title."""
        extractor = PaperExtractor(agent=mock_agent(SAMPLE_PAPER_RESULT))
        result = await extractor.extract({"text": "..."})

        proposes = [r for r in result.relationships if r["type"] == "PROPOSES"]
        assert len(proposes) == 3
        targets = {r["target"] for r in proposes}
        assert targets == {"ReAct", "ChainOfThought", "ToolCalling"}
        assert all(r["source"] == "ReAct: Synergizing Reasoning and Acting in Language Models" for r in proposes)

    @pytest.mark.asyncio
    async def test_extract_handles_empty_concepts(self):
        """Empty concepts list produces no concept entities."""
        result = PaperResult(
            title="Test Paper",
            authors=[],
            abstract="",
            concepts=[],
            frameworks=[],
            contribution_type="method",
        )
        extractor = PaperExtractor(agent=mock_agent(result))
        extraction = await extractor.extract({"text": "..."})

        concept_entities = [e for e in extraction.entities if e["type"] == "concept"]
        assert len(concept_entities) == 0

    @pytest.mark.asyncio
    async def test_extract_returns_empty_on_llm_failure(self):
        """When LLM raises an exception, empty ExtractionResult is returned."""
        extractor = PaperExtractor(agent=mock_agent_failure())
        result = await extractor.extract({"text": "..."})

        assert result.entities == []
        assert result.relationships == []

    @pytest.mark.asyncio
    async def test_extract_returns_empty_on_empty_title(self):
        """When LLM returns result with empty title, empty ExtractionResult is returned."""
        result = PaperResult(
            title="",
            authors=[],
            abstract="",
            concepts=[],
            frameworks=[],
            contribution_type="method",
        )
        extractor = PaperExtractor(agent=mock_agent(result))
        extraction = await extractor.extract({"text": "..."})

        assert extraction.entities == []


# ---------------------------------------------------------------------------
# ConceptExtractor
# ---------------------------------------------------------------------------


SAMPLE_CONCEPT_RESULT = ConceptResult(
    concepts=[
        ExtractedConcept(name="ReAct", description="Synergizes reasoning and acting", category="reasoning"),
        ExtractedConcept(name="ChainOfThought", description="Step-by-step reasoning", category="reasoning"),
        ExtractedConcept(name="ToolCalling", description="LLM invokes external tools", category="tool_use"),
    ],
)


class TestConceptExtractor:
    """Tests for ConceptExtractor at the extract() seam."""

    @pytest.mark.asyncio
    async def test_extract_returns_concept_entities(self):
        """Each concept from LLM response becomes an entity."""
        extractor = ConceptExtractor(agent=mock_agent(SAMPLE_CONCEPT_RESULT))
        result = await extractor.extract({"text": "ReAct uses ChainOfThought..."})

        assert result.source == "concept"
        assert len(result.entities) == 3
        names = {e["name"] for e in result.entities}
        assert names == {"ReAct", "ChainOfThought", "ToolCalling"}

    @pytest.mark.asyncio
    async def test_extract_preserves_category_and_description(self):
        """Each concept entity retains its category and description."""
        extractor = ConceptExtractor(agent=mock_agent(SAMPLE_CONCEPT_RESULT))
        result = await extractor.extract({"text": "..."})

        react = next(e for e in result.entities if e["name"] == "ReAct")
        assert react["category"] == "reasoning"
        assert react["description"] == "Synergizes reasoning and acting"

    @pytest.mark.asyncio
    async def test_extract_creates_related_to_between_coconcepts(self):
        """Co-occurring concepts get RELATED_TO relationships (pairwise)."""
        extractor = ConceptExtractor(agent=mock_agent(SAMPLE_CONCEPT_RESULT))
        result = await extractor.extract({"text": "..."})

        related = [r for r in result.relationships if r["type"] == "RELATED_TO"]
        # C(3,2) = 3 pairs
        assert len(related) == 3
        pairs = {(r["source"], r["target"]) for r in related}
        expected = {
            ("ReAct", "ChainOfThought"),
            ("ReAct", "ToolCalling"),
            ("ChainOfThought", "ToolCalling"),
        }
        assert pairs == expected

    @pytest.mark.asyncio
    async def test_extract_skips_empty_concept_names(self):
        """Concepts with empty names are filtered out."""
        result = ConceptResult(
            concepts=[
                ExtractedConcept(name="ReAct", description="test", category="reasoning"),
                ExtractedConcept(name="", description="empty", category="memory"),
                ExtractedConcept(name="  ", description="whitespace", category="memory"),
            ],
        )
        extractor = ConceptExtractor(agent=mock_agent(result))
        extraction = await extractor.extract({"text": "..."})

        assert len(extraction.entities) == 1
        assert extraction.entities[0]["name"] == "ReAct"

    @pytest.mark.asyncio
    async def test_extract_returns_empty_on_llm_failure(self):
        """When LLM raises an exception, empty ExtractionResult is returned."""
        extractor = ConceptExtractor(agent=mock_agent_failure())
        result = await extractor.extract({"text": "..."})

        assert result.entities == []
        assert result.relationships == []


# ---------------------------------------------------------------------------
# RelationshipExtractor
# ---------------------------------------------------------------------------


SAMPLE_RELATIONSHIP_RESULT = RelationshipResult(
    relationships=[
        ExtractedRelationship(source="ReAct", target="ChainOfThought", type="EXTENDS", evidence="ReAct extends CoT"),
        ExtractedRelationship(source="Reflexion", target="ReAct", type="INSPIRED_BY", evidence="Reflexion builds on ReAct"),
    ],
)


class TestRelationshipExtractor:
    """Tests for RelationshipExtractor at the extract() seam."""

    @pytest.mark.asyncio
    async def test_extract_returns_relationships(self):
        """Extracted relationships are returned with correct fields."""
        extractor = RelationshipExtractor(agent=mock_agent(SAMPLE_RELATIONSHIP_RESULT))
        result = await extractor.extract({"text": "..."})

        assert result.source == "relationship"
        assert len(result.relationships) == 2

    @pytest.mark.asyncio
    async def test_extract_validates_relationship_types(self):
        """Invalid relationship types fall back to RELATED_TO."""
        result = RelationshipResult(
            relationships=[
                ExtractedRelationship(source="A", target="B", type="INVALID_TYPE"),
            ],
        )
        extractor = RelationshipExtractor(agent=mock_agent(result))
        extraction = await extractor.extract({"text": "..."})

        assert extraction.relationships[0]["type"] == "RELATED_TO"

    @pytest.mark.asyncio
    async def test_extract_skips_empty_source_or_target(self):
        """Relationships with empty source or target are filtered out."""
        result = RelationshipResult(
            relationships=[
                ExtractedRelationship(source="", target="B", type="RELATED_TO"),
                ExtractedRelationship(source="A", target="", type="RELATED_TO"),
                ExtractedRelationship(source="C", target="D", type="RELATED_TO"),
            ],
        )
        extractor = RelationshipExtractor(agent=mock_agent(result))
        extraction = await extractor.extract({"text": "..."})

        assert len(extraction.relationships) == 1
        assert extraction.relationships[0]["source"] == "C"

    @pytest.mark.asyncio
    async def test_extract_returns_empty_on_llm_failure(self):
        """When LLM raises an exception, empty ExtractionResult is returned."""
        extractor = RelationshipExtractor(agent=mock_agent_failure())
        result = await extractor.extract({"text": "..."})

        assert result.entities == []
        assert result.relationships == []
