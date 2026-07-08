"""Tests for QueryRouter — query classification and weight selection."""

import pytest

from agentverse.graphrag.retrieval.router import QueryRouter, FusionWeights


@pytest.fixture
def router():
    return QueryRouter()


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


class TestQueryRouterClassification:
    """Tests for query intent classification."""

    def test_empty_query_returns_default(self, router):
        assert router.classify("") == "default"
        assert router.classify("   ") == "default"

    def test_structural_depend_pattern(self, router):
        assert router.classify("what frameworks depend on LangChain") == "structural"

    def test_structural_implement_pattern(self, router):
        assert router.classify("which tools implement chain-of-thought") == "structural"

    def test_structural_extend_pattern(self, router):
        assert router.classify("ReAct extends ChainOfThought") == "structural"

    def test_structural_evolve_pattern(self, router):
        assert router.classify("how did reasoning evolve") == "structural"

    def test_structural_related_pattern(self, router):
        assert router.classify("what is related to GraphRAG") == "structural"

    def test_structural_which_uses_pattern(self, router):
        assert router.classify("which agents use tool calling") == "structural"

    def test_structural_built_on_pattern(self, router):
        assert router.classify("frameworks built on LangChain") == "structural"

    def test_structural_graph_pattern(self, router):
        assert router.classify("show the dependency graph") == "structural"

    def test_structural_between_pattern(self, router):
        assert router.classify("connection from ReAct to Reflexion") == "structural"

    def test_semantic_what_is_pattern(self, router):
        # "what is" matches semantic, but "depend" also appears → structural wins
        # Let's use a clean semantic query
        assert router.classify("what is chain-of-thought reasoning") == "default"

    def test_semantic_explain_pattern(self, router):
        assert router.classify("explain the ReAct framework") == "default"

    def test_semantic_how_does_pattern(self, router):
        assert router.classify("how does GraphRAG work") == "default"

    def test_default_unknown_query(self, router):
        assert router.classify("LangChain") == "default"
        assert router.classify("AI agents 2024") == "default"

    def test_structural_beats_semantic(self, router):
        """When both patterns match, structural wins."""
        result = router.classify("what frameworks depend on each other")
        assert result == "structural"


# ---------------------------------------------------------------------------
# Weight selection
# ---------------------------------------------------------------------------


class TestQueryRouterWeights:
    """Tests for weight selection."""

    def test_default_weights(self, router):
        w = router.weights("random query")
        assert w.vector == pytest.approx(0.6)
        assert w.graph == pytest.approx(0.4)

    def test_structural_weights(self, router):
        w = router.weights("what depends on LangChain")
        assert w.vector == pytest.approx(0.3)
        assert w.graph == pytest.approx(0.7)

    def test_semantic_query_gets_default_weights(self, router):
        """Semantic queries map to default (0.6/0.4) since vector already dominant."""
        w = router.weights("what is chain-of-thought")
        assert w.vector == pytest.approx(0.6)
        assert w.graph == pytest.approx(0.4)

    def test_weights_are_frozen(self, router):
        """FusionWeights should be immutable."""
        w = router.weights("test")
        assert isinstance(w, FusionWeights)
        with pytest.raises(AttributeError):
            w.vector = 0.9
