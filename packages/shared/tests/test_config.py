"""Tests for shared config module."""

import os
from unittest.mock import patch

from agentverse.shared.config import Settings


def test_settings_defaults():
    """Settings should have sensible defaults."""
    settings = Settings()
    assert settings.environment in ("development", "production")
    assert settings.neo4j_uri  # Should not be empty
    assert settings.postgres_dsn  # Should not be empty


def test_settings_from_env(monkeypatch):
    """Settings should be overridden by environment variables."""
    monkeypatch.setenv("NEO4J_URI", "bolt://test:7687")
    settings = Settings()
    assert settings.neo4j_uri == "bolt://test:7687"


def test_settings_llm_config():
    """Settings should have LLM configuration fields."""
    settings = Settings()
    assert hasattr(settings, "openai_api_key")
    assert hasattr(settings, "anthropic_api_key")
    assert hasattr(settings, "embedding_model")
    assert hasattr(settings, "embedding_dimension")
