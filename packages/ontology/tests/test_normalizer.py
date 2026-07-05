"""Tests for ontology normalizer."""

from agentverse.ontology.normalizer import (
    normalize_agent,
    normalize_framework,
    normalize_paper,
    normalize_protocol,
    normalize_news,
    normalize_product,
    normalize_company,
    normalize_memory_type,
    normalize_memory_framework,
    normalize_application,
    normalize_pattern,
    normalize_industry_trend,
)


def test_normalize_agent():
    result = normalize_agent({"name": "ReAct", "description": "desc"})
    assert result.name == "ReAct"
    assert "Agent" in result.labels


def test_normalize_framework():
    result = normalize_framework({"name": "LangGraph", "description": "desc"})
    assert result.name == "LangGraph"
    assert "Framework" in result.labels


def test_normalize_paper():
    result = normalize_paper({"title": "Test Paper", "doi": "10.1234", "abstract": "abs"})
    assert result.name == "Test Paper"
    assert "Paper" in result.labels


def test_normalize_protocol():
    result = normalize_protocol({"name": "MCP", "description": "desc"})
    assert "Protocol" in result.labels


def test_normalize_news():
    result = normalize_news({"title": "News", "url": "http://test", "source": "src"})
    assert result.name == "News"


def test_normalize_product():
    result = normalize_product({"name": "Claude", "company": "Anthropic"})
    assert result.name == "Claude"


def test_normalize_company():
    result = normalize_company({"name": "OpenAI"})
    assert result.name == "OpenAI"


def test_normalize_memory_type():
    result = normalize_memory_type({"name": "Episodic", "memory_category": "short-term"})
    assert result.name == "Episodic"


def test_normalize_memory_framework():
    result = normalize_memory_framework({"name": "Mem0", "github_url": "http://gh"})
    assert result.name == "Mem0"


def test_normalize_application():
    result = normalize_application({"name": "Cursor", "tech_stack": "VSCode"})
    assert result.name == "Cursor"


def test_normalize_pattern():
    result = normalize_pattern({"name": "ReAct Pattern"})
    assert result.name == "ReAct Pattern"


def test_normalize_industry_trend():
    result = normalize_industry_trend({"name": "Rise of Agents", "direction": "up"})
    assert result.name == "Rise of Agents"
