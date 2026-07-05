"""Tests for ontology concepts."""

from agentverse.ontology.concepts.base import Concept
from agentverse.ontology.concepts.agent import AgentConcept
from agentverse.ontology.concepts.framework import FrameworkConcept
from agentverse.ontology.concepts.paper import PaperConcept


def test_concept_base():
    """Concept base should set labels and properties."""
    c = Concept(name="Test", description="desc", category="test")
    assert c.labels == ["Concept"]
    assert c.properties["name"] == "Test"


def test_agent_concept():
    """AgentConcept should have Agent label."""
    c = AgentConcept(name="ReAct", description="Reasoning + Acting")
    assert "Agent" in c.labels
    assert "Concept" in c.labels
    assert c.category == "agent"


def test_framework_concept():
    """FrameworkConcept should have Framework label."""
    c = FrameworkConcept(name="LangGraph")
    assert "Framework" in c.labels


def test_paper_concept():
    """PaperConcept should have Paper label."""
    c = PaperConcept(name="ReAct Paper", doi="10.1234/test")
    assert "Paper" in c.labels
    assert c.properties.get("doi") == "10.1234/test"
