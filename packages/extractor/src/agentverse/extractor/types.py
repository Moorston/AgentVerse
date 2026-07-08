"""TypedDict and Pydantic model definitions for extractor data structures."""

from typing import TypedDict

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request type (unchanged)
# ---------------------------------------------------------------------------


class ExtractionRequest(TypedDict, total=False):
    """Typed request parameters for extractor.extract() methods.

    All fields are optional. Each extractor extracts the subset it supports
    and ignores the rest.
    """

    text: str
    source: str
    max_concepts: int
    categories: list[str]


# ---------------------------------------------------------------------------
# Pydantic result types (used by PydanticAI agents)
# ---------------------------------------------------------------------------

VALID_CATEGORIES = [
    "reasoning",
    "planning",
    "memory",
    "tool_use",
    "reflection",
    "multi_agent",
    "workflow",
    "protocol",
    "rag",
    "prompt_engineering",
]

VALID_RELATIONSHIP_TYPES = [
    "PROPOSES",
    "IMPLEMENTS",
    "EVOLVES_TO",
    "RELATED_TO",
    "DEPENDS_ON",
    "SUPPORTS",
    "USED_IN",
    "REFERENCES",
    "CITES",
    "EXTENDS",
    "INSPIRED_BY",
]


class ExtractedConcept(BaseModel):
    """A single concept extracted by the LLM."""

    name: str = Field(description="PascalCase concept name (e.g. ChainOfThought)")
    description: str = Field(default="", description="One-sentence description")
    category: str = Field(default="reasoning", description="Concept category")


class ExtractedRelationship(BaseModel):
    """A single relationship extracted by the LLM."""

    source: str = Field(description="PascalCase source entity name")
    target: str = Field(description="PascalCase target entity name")
    type: str = Field(default="RELATED_TO", description="Relationship type")
    evidence: str = Field(default="", description="Brief evidence from text")


class PaperResult(BaseModel):
    """Structured result from paper extraction."""

    title: str = Field(description="Paper title")
    authors: list[str] = Field(default_factory=list, description="Author names")
    abstract: str = Field(default="", description="Paper abstract")
    concepts: list[ExtractedConcept] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list, description="Related framework names")
    contribution_type: str = Field(default="method", description="method|survey|benchmark|analysis|system")


class ConceptResult(BaseModel):
    """Structured result from concept extraction."""

    concepts: list[ExtractedConcept] = Field(default_factory=list)


class RelationshipResult(BaseModel):
    """Structured result from relationship extraction."""

    relationships: list[ExtractedRelationship] = Field(default_factory=list)
