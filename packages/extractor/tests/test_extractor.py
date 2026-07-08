"""Tests for LLM client factory and prompts."""

from unittest.mock import patch

from agentverse.extractor.llm.client import LLMClient
from agentverse.extractor.llm.prompts import (
    PAPER_EXTRACTION_PROMPT,
    CONCEPT_EXTRACTION_PROMPT,
    RELATIONSHIP_EXTRACTION_PROMPT,
)
from agentverse.extractor.types import PaperResult, ConceptResult, RelationshipResult


# ---------------------------------------------------------------------------
# LLMClient (factory)
# ---------------------------------------------------------------------------


class TestLLMClient:
    """Tests for the PydanticAI Agent factory."""

    def test_creates_agent_instance(self):
        """LLMClient.get_agent returns a PydanticAI Agent."""
        with patch("agentverse.extractor.llm.client.Settings") as MockSettings:
            MockSettings.return_value = type("S", (), {
                "openai_api_key": "sk-test",
                "openai_model": "gpt-4o",
                "openai_base_url": "",
                "anthropic_api_key": "",
                "anthropic_model": "claude-sonnet-4-20250514",
            })()
            client = LLMClient()
            # Patch _resolve_model to avoid real model inference
            with patch.object(client, "_resolve_model", return_value="test-model"):
                with patch("agentverse.extractor.llm.client.Agent") as MockAgent:
                    MockAgent.return_value = "mock-agent"
                    result = client.get_agent(
                        result_type=PaperResult,
                        system_prompt="test",
                    )
                    assert result == "mock-agent"
                    MockAgent.assert_called_once_with(
                        "test-model",
                        result_type=PaperResult,
                        system_prompt="test",
                        retries=3,
                    )

    def test_resolve_model_openai(self):
        """OpenAI key present → model string starts with 'openai:'."""
        with patch("agentverse.extractor.llm.client.Settings") as MockSettings:
            MockSettings.return_value = type("S", (), {
                "openai_api_key": "sk-test",
                "openai_model": "gpt-4o",
                "openai_base_url": "",
                "anthropic_api_key": "",
                "anthropic_model": "claude-sonnet-4-20250514",
            })()
            client = LLMClient()
            model = client._resolve_model()
            assert model == "openai:gpt-4o"

    def test_resolve_model_anthropic_fallback(self):
        """No OpenAI key → falls back to Anthropic."""
        with patch("agentverse.extractor.llm.client.Settings") as MockSettings:
            MockSettings.return_value = type("S", (), {
                "openai_api_key": "",
                "openai_model": "gpt-4o",
                "openai_base_url": "",
                "anthropic_api_key": "sk-ant-test",
                "anthropic_model": "claude-sonnet-4-20250514",
            })()
            client = LLMClient()
            model = client._resolve_model()
            assert model == "anthropic:claude-sonnet-4-20250514"


# ---------------------------------------------------------------------------
# Prompts (unchanged)
# ---------------------------------------------------------------------------


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
