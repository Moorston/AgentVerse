"""Tests for GraphSearch — knowledge graph traversal search."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from agentverse.graph_core.client import GraphClient
from agentverse.graphrag.retrieval.graph import GraphSearch


@pytest.fixture
def mock_client():
    """Fixture: mock GraphClient."""
    client = MagicMock(spec=GraphClient)
    return client


@pytest.fixture
def graph_search(mock_client):
    """Fixture: GraphSearch with mocked client."""
    return GraphSearch(mock_client)


class TestGraphSearchExactMatch:
    """Tests for exact name match strategy."""

    @pytest.mark.asyncio
    async def test_returns_exact_match_results(self, mock_client, graph_search):
        mock_client.execute = AsyncMock(
            side_effect=[
                # Strategy 1: exact match — returns results
                [
                    {
                        "n": {"name": "LangChain", "description": "LLM framework"},
                        "connections": [],
                    }
                ],
                # Strategy 2: fuzzy — skipped because top_k already met
                [],
                # Strategy 3: multi-hop — not called (empty result for exact)
                [],
            ]
        )

        results = await graph_search.search("LangChain", top_k=10)

        assert len(results) >= 1
        assert results[0]["match_type"] == "exact"
        assert results[0]["node"]["name"] == "LangChain"
        assert results[0]["score"] == 1.0

    @pytest.mark.asyncio
    async def test_exact_query_uses_cypher_parameters(self, mock_client, graph_search):
        mock_client.execute = AsyncMock(return_value=[])
        await graph_search.search("TestQuery", top_k=5)

        # First call should use correct query with $query and $limit
        call = mock_client.execute.call_args_list[0]
        cql, params = call[0][0], call[0][1]
        assert params == {"query": "TestQuery", "limit": 5}
        assert "$query" in cql
        assert "$limit" in cql


class TestGraphSearchFuzzyMatch:
    """Tests for fuzzy (CONTAINS) match strategy."""

    @pytest.mark.asyncio
    async def test_fuzzy_called_when_exact_returns_few(self, mock_client, graph_search):
        mock_client.execute = AsyncMock(
            side_effect=[
                # Strategy 1: exact — 1 result (below top_k=5)
                [
                    {
                        "n": {"name": "Agent", "description": "AI agent framework"},
                        "connections": [],
                    }
                ],
                # Strategy 2: fuzzy — 2 results
                [
                    {
                        "n": {"name": "AutoGen", "description": "multi-agent"},
                        "connections": [],
                    },
                    {
                        "n": {"name": "CrewAI", "description": "crew-based agent"},
                        "connections": [],
                    },
                ],
                # Strategy 3: multi-hop — not called (already >= results)
                [],
            ]
        )

        results = await graph_search.search("Agent", top_k=5)

        assert len(results) == 3
        fuzzy_results = [r for r in results if r["match_type"] == "fuzzy"]
        assert len(fuzzy_results) == 2
        assert all(r["score"] == 0.7 for r in fuzzy_results)

    @pytest.mark.asyncio
    async def test_fuzzy_limit_is_adjusted(self, mock_client, graph_search):
        mock_client.execute = AsyncMock(
            side_effect=[
                # Exact returns 1
                [{"n": {"name": "LLM"}, "connections": []}],
                # Fuzzy — should have limit=4 (top_k=5 - 1 exact)
                [],
                [],
            ]
        )

        await graph_search.search("LLM", top_k=5)

        fuzzy_call = mock_client.execute.call_args_list[1]
        _, params = fuzzy_call[0][0], fuzzy_call[0][1]
        assert params["limit"] == 4


class TestGraphSearchMultiHop:
    """Tests for multi-hop traversal strategy."""

    @pytest.mark.asyncio
    async def test_multi_hop_from_top_result(self, mock_client, graph_search):
        mock_client.execute = AsyncMock(
            side_effect=[
                # Strategy 1: exact
                [
                    {
                        "n": {"name": "LangChain", "description": "LLM framework"},
                        "connections": [],
                    }
                ],
                # Strategy 2: fuzzy — 0 results
                [],
                # Strategy 3: multi-hop — 2 neighbors
                [
                    {
                        "path_nodes": [
                            {"name": "LangChain"},
                            {"name": "LLM"},
                        ],
                        "path_rels": [{"type": "RELATED_TO"}],
                    },
                    {
                        "path_nodes": [
                            {"name": "LangChain"},
                            {"name": "Agent"},
                        ],
                        "path_rels": [{"type": "CONTAINS"}],
                    },
                ],
            ]
        )

        results = await graph_search.search("LangChain", top_k=5, max_depth=3)

        traversal_results = [r for r in results if r["match_type"] == "traversal"]
        assert len(traversal_results) == 2
        assert all(r["score"] == 0.5 for r in traversal_results)

    @pytest.mark.asyncio
    async def test_multi_hop_respects_max_depth(self, mock_client, graph_search):
        mock_client.execute = AsyncMock(
            side_effect=[
                [{"n": {"name": "Test"}, "connections": []}],
                [],
                [],
            ]
        )

        await graph_search.search("Test", top_k=5, max_depth=2)

        traversal_call = mock_client.execute.call_args_list[2]
        cql, _ = traversal_call[0][0], traversal_call[0][1]
        assert "[*1..2]" in cql

    @pytest.mark.asyncio
    async def test_multi_hop_not_called_when_no_exact_results(self, mock_client, graph_search):
        mock_client.execute = AsyncMock(
            side_effect=[
                [],  # exact — empty
                [],  # fuzzy — empty
            ]
        )

        await graph_search.search("Unknown", top_k=5)

        # Only 2 calls (exact + fuzzy), no multi-hop
        assert mock_client.execute.call_count == 2