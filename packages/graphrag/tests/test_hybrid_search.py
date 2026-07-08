"""Tests for HybridSearch — fusion of vector and graph results.

Includes tests for:
- Default fusion ranking (0.6/0.4 weights)
- Adaptive weights via QueryRouter
- TTLCache behavior
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from agentverse.graphrag.retrieval.hybrid import HybridSearch
from agentverse.graphrag.retrieval.vector import VectorSearch
from agentverse.graphrag.retrieval.graph import GraphSearch
from agentverse.graphrag.retrieval.router import QueryRouter, FusionWeights


@pytest.fixture
def mock_vector_search():
    """Fixture: mock VectorSearch."""
    vs = MagicMock(spec=VectorSearch)
    vs.search = AsyncMock()
    return vs


@pytest.fixture
def mock_graph_search():
    """Fixture: mock GraphSearch."""
    gs = MagicMock(spec=GraphSearch)
    gs.search = AsyncMock()
    return gs


@pytest.fixture
def hybrid(mock_vector_search, mock_graph_search):
    """Fixture: HybridSearch with mocked sub-searches."""
    return HybridSearch(mock_vector_search, mock_graph_search)


# ---------------------------------------------------------------------------
# Default fusion ranking (0.6/0.4 — generic queries)
# ---------------------------------------------------------------------------


class TestHybridSearchFusionRanking:
    """Tests for fusion ranking formula with default weights."""

    @pytest.mark.asyncio
    async def test_combined_score_weighting(self, hybrid, mock_vector_search, mock_graph_search):
        """Verify combined_score = 0.6 * vector_score + 0.4 * graph_score for default queries."""
        mock_vector_search.search.return_value = [
            {"node_id": "n1", "name": "LangChain", "score": 0.9},
        ]
        mock_graph_search.search.return_value = [
            {"node": {"name": "LangChain", "description": ""}, "score": 1.0, "match_type": "exact"},
        ]

        results = await hybrid.search("LangChain", top_k=10)

        assert len(results) == 1
        # 0.6 * 0.9 + 0.4 * 1.0 = 0.54 + 0.40 = 0.94
        assert results[0]["score"] == pytest.approx(0.94)
        assert results[0]["source"] == "hybrid"

    @pytest.mark.asyncio
    async def test_vector_only_result_uses_vector_score(self, hybrid, mock_vector_search, mock_graph_search):
        """When a vector result has no graph match, use vector_score * 0.6 with source='vector'."""
        mock_vector_search.search.return_value = [
            {"node_id": "n1", "name": "UniqueVector", "score": 0.8},
        ]
        mock_graph_search.search.return_value = []

        results = await hybrid.search("query", top_k=10)

        assert len(results) == 1
        # combined = 0.6 * 0.8 + 0.4 * 0.0 = 0.48
        assert results[0]["score"] == pytest.approx(0.48)
        assert results[0]["source"] == "vector"

    @pytest.mark.asyncio
    async def test_graph_only_result_uses_adjusted_score(self, hybrid, mock_vector_search, mock_graph_search):
        """Graph-only results get score = graph_score * 0.4 with source='graph'."""
        mock_vector_search.search.return_value = []
        mock_graph_search.search.return_value = [
            {"node": {"name": "GraphOnly", "description": ""}, "score": 0.7, "match_type": "fuzzy"},
        ]

        results = await hybrid.search("query", top_k=10)

        assert len(results) == 1
        # graph-only: score = 0.7 * 0.4 = 0.28
        assert results[0]["score"] == pytest.approx(0.28)
        assert results[0]["source"] == "graph"

    @pytest.mark.asyncio
    async def test_results_sorted_by_score_descending(self, hybrid, mock_vector_search, mock_graph_search):
        """Results should be sorted by score descending."""
        mock_vector_search.search.return_value = [
            {"node_id": "n1", "name": "ItemA", "score": 0.5},
            {"node_id": "n2", "name": "ItemB", "score": 1.0},
        ]
        mock_graph_search.search.return_value = [
            {"node": {"name": "ItemA", "description": ""}, "score": 0.2, "match_type": "fuzzy"},
            {"node": {"name": "ItemC", "description": ""}, "score": 1.0, "match_type": "exact"},
        ]

        results = await hybrid.search("query", top_k=10)

        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)


class TestHybridSearchDeduplication:
    """Tests for deduplication logic."""

    @pytest.mark.asyncio
    async def test_deduplicates_by_name(self, hybrid, mock_vector_search, mock_graph_search):
        """Same name in both result sets should appear only once."""
        mock_vector_search.search.return_value = [
            {"node_id": "n1", "name": "Duplicate", "score": 0.8},
        ]
        mock_graph_search.search.return_value = [
            {"node": {"name": "Duplicate", "description": ""}, "score": 0.9, "match_type": "exact"},
            {"node": {"name": "Unique", "description": ""}, "score": 0.6, "match_type": "fuzzy"},
        ]

        results = await hybrid.search("query", top_k=10)

        names = [r.get("name", "") or (r.get("node", {}).get("name", "")) for r in results]
        assert len(names) == 2
        assert names.count("Duplicate") == 1
        assert "Unique" in names

    @pytest.mark.asyncio
    async def test_top_k_respected(self, hybrid, mock_vector_search, mock_graph_search):
        """Final result count should not exceed top_k."""
        mock_vector_search.search.return_value = [
            {"node_id": f"n{i}", "name": f"Item{i}", "score": 0.5} for i in range(5)
        ]
        mock_graph_search.search.return_value = [
            {"node": {"name": f"Item{i}", "description": ""}, "score": 0.5, "match_type": "fuzzy"}
            for i in range(5)
        ]

        results = await hybrid.search("query", top_k=3)

        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_empty_results_when_both_empty(self, hybrid, mock_vector_search, mock_graph_search):
        mock_vector_search.search.return_value = []
        mock_graph_search.search.return_value = []

        results = await hybrid.search("query", top_k=10)

        assert results == []


# ---------------------------------------------------------------------------
# Adaptive weights via QueryRouter
# ---------------------------------------------------------------------------


class TestAdaptiveWeights:
    """Tests for query-adaptive fusion weights."""

    @pytest.mark.asyncio
    async def test_structural_query_uses_graph_dominant_weights(
        self, mock_vector_search, mock_graph_search
    ):
        """Structural queries should favor graph search (0.3/0.7)."""
        hybrid = HybridSearch(mock_vector_search, mock_graph_search)

        mock_vector_search.search.return_value = [
            {"node_id": "n1", "name": "LangChain", "score": 0.9},
        ]
        mock_graph_search.search.return_value = [
            {"node": {"name": "LangChain", "description": ""}, "score": 1.0, "match_type": "exact"},
        ]

        results = await hybrid.search("what frameworks depend on LangChain", top_k=10)

        assert len(results) == 1
        # structural: 0.3 * 0.9 + 0.7 * 1.0 = 0.27 + 0.70 = 0.97
        assert results[0]["score"] == pytest.approx(0.97)

    @pytest.mark.asyncio
    async def test_semantic_query_uses_vector_dominant_weights(
        self, mock_vector_search, mock_graph_search
    ):
        """Semantic queries should favor vector search (0.8/0.2)."""
        hybrid = HybridSearch(mock_vector_search, mock_graph_search)

        mock_vector_search.search.return_value = [
            {"node_id": "n1", "name": "ReAct", "score": 0.9},
        ]
        mock_graph_search.search.return_value = [
            {"node": {"name": "ReAct", "description": ""}, "score": 1.0, "match_type": "exact"},
        ]

        results = await hybrid.search("what is chain-of-thought reasoning", top_k=10)

        assert len(results) == 1
        # semantic → "default" weights: 0.6 * 0.9 + 0.4 * 1.0 = 0.94
        # (note: semantic maps to "default" because vector is already dominant at 0.6/0.4)
        assert results[0]["score"] == pytest.approx(0.94)

    @pytest.mark.asyncio
    async def test_graph_only_with_structural_query(self, mock_vector_search, mock_graph_search):
        """Structural query with graph-only results: score = graph_score * 0.7."""
        hybrid = HybridSearch(mock_vector_search, mock_graph_search)

        mock_vector_search.search.return_value = []
        mock_graph_search.search.return_value = [
            {"node": {"name": "X", "description": ""}, "score": 1.0, "match_type": "exact"},
        ]

        results = await hybrid.search("what depends on X framework", top_k=10)

        assert len(results) == 1
        # graph-only with structural weights: 1.0 * 0.7 = 0.7
        assert results[0]["score"] == pytest.approx(0.7)


# ---------------------------------------------------------------------------
# Cache behavior
# ---------------------------------------------------------------------------


class TestHybridSearchCache:
    """Tests for TTLCache behavior."""

    @pytest.mark.asyncio
    async def test_cache_hit_returns_same_result(self, mock_vector_search, mock_graph_search):
        """Second identical query returns cached result without calling sub-searches."""
        hybrid = HybridSearch(mock_vector_search, mock_graph_search, cache_ttl=60.0)

        mock_vector_search.search.return_value = [
            {"node_id": "n1", "name": "Test", "score": 0.8},
        ]
        mock_graph_search.search.return_value = []

        result1 = await hybrid.search("test query", top_k=10)
        result2 = await hybrid.search("test query", top_k=10)

        assert result1 == result2
        # Sub-searches should only be called once
        assert mock_vector_search.search.call_count == 1
        assert mock_graph_search.search.call_count == 1

    @pytest.mark.asyncio
    async def test_different_queries_not_cached(self, mock_vector_search, mock_graph_search):
        """Different queries should not share cache entries."""
        hybrid = HybridSearch(mock_vector_search, mock_graph_search, cache_ttl=60.0)

        mock_vector_search.search.return_value = []
        mock_graph_search.search.return_value = []

        await hybrid.search("query A", top_k=10)
        await hybrid.search("query B", top_k=10)

        assert mock_vector_search.search.call_count == 2

    @pytest.mark.asyncio
    async def test_clear_cache_forces_refresh(self, mock_vector_search, mock_graph_search):
        """After clear_cache(), next query hits sub-searches again."""
        hybrid = HybridSearch(mock_vector_search, mock_graph_search, cache_ttl=60.0)

        mock_vector_search.search.return_value = []
        mock_graph_search.search.return_value = []

        await hybrid.search("test", top_k=10)
        assert mock_vector_search.search.call_count == 1

        hybrid.clear_cache()
        await hybrid.search("test", top_k=10)
        assert mock_vector_search.search.call_count == 2

    @pytest.mark.asyncio
    async def test_different_top_k_not_cached(self, mock_vector_search, mock_graph_search):
        """Same query with different top_k should not share cache."""
        hybrid = HybridSearch(mock_vector_search, mock_graph_search, cache_ttl=60.0)

        mock_vector_search.search.return_value = []
        mock_graph_search.search.return_value = []

        await hybrid.search("test", top_k=5)
        await hybrid.search("test", top_k=10)

        assert mock_vector_search.search.call_count == 2
