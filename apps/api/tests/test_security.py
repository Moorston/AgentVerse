"""Tests for security validation and sanitization."""

import pytest

from agentverse.api.core.security import (
    sanitize_name,
    validate_name,
    validate_query,
    sanitize_properties,
)


class TestSanitizeName:
    """Tests for sanitize_name function."""

    def test_strips_whitespace(self):
        assert sanitize_name("  hello  ") == "hello"

    def test_removes_control_characters(self):
        assert sanitize_name("hello\x00world") == "helloworld"
        assert sanitize_name("test\x1ftext") == "testtext"

    def test_limits_length(self):
        long_name = "a" * 600
        assert len(sanitize_name(long_name)) == 500

    def test_empty_string(self):
        assert sanitize_name("") == ""

    def test_normal_name_unchanged(self):
        assert sanitize_name("Chain-of-Thought") == "Chain-of-Thought"

    def test_preserves_unicode(self):
        assert sanitize_name("AI代理概念") == "AI代理概念"


class TestValidateName:
    """Tests for validate_name function."""

    def test_valid_name(self):
        valid, error = validate_name("AgentVerse")
        assert valid is True
        assert error == ""

    def test_empty_name_rejected(self):
        valid, error = validate_name("")
        assert valid is False
        assert "empty" in error.lower()

    def test_long_name_rejected(self):
        valid, error = validate_name("a" * 501)
        assert valid is False
        assert "long" in error.lower()

    def test_cypher_injection_semicolon(self):
        valid, error = validate_name("test; MATCH (n) DETACH DELETE n")
        assert valid is False

    def test_cypher_injection_comment(self):
        valid, error = validate_name("test // malicious")
        assert valid is False

    def test_normal_names_accepted(self):
        for name in ["ReAct", "LangGraph", "AutoGen", "GPT-4", "Agent (v2)"]:
            valid, _ = validate_name(name)
            assert valid is True, f"'{name}' should be valid"


class TestValidateQuery:
    """Tests for validate_query function."""

    def test_valid_query(self):
        valid, error = validate_query("agent reasoning planning")
        assert valid is True

    def test_empty_query_valid(self):
        valid, error = validate_query("")
        assert valid is True

    def test_long_query_rejected(self):
        valid, error = validate_query("a" * 1001)
        assert valid is False
        assert "long" in error.lower()

    def test_xss_script_tag(self):
        valid, error = validate_query('<script>alert("xss")</script>')
        assert valid is False

    def test_xss_event_handler(self):
        valid, error = validate_query('onerror=alert(1)')
        assert valid is False

    def test_xss_iframe(self):
        valid, error = validate_query('<iframe src="evil.com">')
        assert valid is False

    def test_normal_query_with_special_chars(self):
        valid, _ = validate_query("what is chain-of-thought (CoT)?")
        assert valid is True


class TestSanitizeProperties:
    """Tests for sanitize_properties function."""

    def test_sanitizes_string_values(self):
        props = {"name": "  test  ", "desc": "hello\x00world"}
        result = sanitize_properties(props)
        assert result["name"] == "test"
        assert result["desc"] == "helloworld"

    def test_sanitizes_list_values(self):
        props = {"tags": ["  tag1  ", "tag2"]}
        result = sanitize_properties(props)
        assert result["tags"] == ["tag1", "tag2"]

    def test_preserves_non_strings(self):
        props = {"count": 42, "active": True, "score": 3.14}
        result = sanitize_properties(props)
        assert result["count"] == 42
        assert result["active"] is True
        assert result["score"] == 3.14

    def test_mixed_types(self):
        props = {
            "name": "  test  ",
            "count": 5,
            "tags": ["  a  ", 42, "  b  "],
        }
        result = sanitize_properties(props)
        assert result["name"] == "test"
        assert result["count"] == 5
        assert result["tags"] == ["a", 42, "b"]