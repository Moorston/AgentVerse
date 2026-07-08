"""Tests for GraphRAGEngine and IndexingPipeline.

Tests at the public seam: query()/reindex() with mocked dependencies.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from agentverse.graphrag.engine import GraphRAGEngine
from agentverse.graphrag.indexing.pipeline import IndexingPipeline
from agentverse.graphrag.embeddings.base import BaseEmbeddingModel
from agentverse.graphrag.retrieval.vector import VectorSearch
from agentverse.graphrag.retrieval.graph import GraphSearch
from agentverse.graphrag.retrieval.hybrid import HybridSearch
from agentverse.graph_core.client import GraphClient


# ---------------------------------------------------------------------------
# GraphRAGEngine
# ---------------------------------------------------------------------------


class TestGraphRAGEngineQuery:
    """Tests for GraphRAGEngine.query() strategy dispatch."""

    def _make_engine(self) -> tuple[GraphRAGEngine, MagicMock, MagicMock, MagicMock]:
        """Create engine with mocked search components."""
        engine = GraphRAGEngine.__new__(GraphRAGEngine)
        engine._settings = None
        engine._client = MagicMock(spec=GraphClient)
        engine._embedding_model = MagicMock(spec=BaseEmbeddingModel)
        engine._vector_store = MagicMock()
        engine._vector_search = MagicMock(spec=VectorSearch)
        engine._vector_search.search = AsyncMock(return_value=[{"name": "vec_result", "score": 0.9}])
        engine._graph_search = MagicMock(spec=GraphSearch)
        engine._graph_search.search = AsyncMock(return_value=[{"name": "graph_result", "score": 0.8}])
        engine._hybrid_search = MagicMock(spec=HybridSearch)
        engine._hybrid_search.search = AsyncMock(return_value=[{"name": "hybrid_result", "score": 0.95}])
        engine._indexing_pipeline = MagicMock(spec=IndexingPipeline)
        engine._indexing_pipeline.run = AsyncMock(return_value=10)
        return engine, engine._vector_search, engine._graph_search, engine._hybrid_search

    @pytest.mark.asyncio
    async def test_query_vector_strategy(self):
        """strategy='vector' delegates to VectorSearch."""
        engine, vs, gs, hs = self._make_engine()

        results = await engine.query("test", top_k=5, strategy="vector")

        vs.search.assert_awaited_once_with("test", 5)
        gs.search.assert_not_awaited()
        hs.search.assert_not_awaited()
        assert results == [{"name": "vec_result", "score": 0.9}]

    @pytest.mark.asyncio
    async def test_query_graph_strategy(self):
        """strategy='graph' delegates to GraphSearch."""
        engine, vs, gs, hs = self._make_engine()

        results = await engine.query("test", top_k=5, strategy="graph")

        gs.search.assert_awaited_once_with("test", 5)
        vs.search.assert_not_awaited()
        hs.search.assert_not_awaited()
        assert results == [{"name": "graph_result", "score": 0.8}]

    @pytest.mark.asyncio
    async def test_query_hybrid_strategy(self):
        """strategy='hybrid' (default) delegates to HybridSearch."""
        engine, vs, gs, hs = self._make_engine()

        results = await engine.query("test", top_k=5)

        hs.search.assert_awaited_once_with("test", 5)
        vs.search.assert_not_awaited()
        gs.search.assert_not_awaited()
        assert results == [{"name": "hybrid_result", "score": 0.95}]

    @pytest.mark.asyncio
    async def test_query_returns_empty_when_not_initialized(self):
        """Engine with no search components returns empty list."""
        engine = GraphRAGEngine.__new__(GraphRAGEngine)
        engine._vector_search = None
        engine._graph_search = None
        engine._hybrid_search = None

        results = await engine.query("test")

        assert results == []


# ---------------------------------------------------------------------------
# IndexingPipeline
# ---------------------------------------------------------------------------


class TestIndexingPipeline:
    """Tests for IndexingPipeline.run()."""

    @pytest.mark.asyncio
    async def test_run_indexes_nodes(self):
        """Pipeline fetches nodes, embeds, and upserts to vector store."""
        mock_client = MagicMock(spec=GraphClient)
        mock_client.execute = AsyncMock(return_value=[
            {"id": "node1", "name": "ReAct", "description": "Reasoning+Acting"},
            {"id": "node2", "name": "ChainOfThought", "description": "Step-by-step"},
        ])

        mock_embedding = MagicMock(spec=BaseEmbeddingModel)
        mock_embedding.embed_batch = AsyncMock(return_value=[[0.1, 0.2], [0.3, 0.4]])

        mock_store = MagicMock()
        mock_store.upsert = AsyncMock()

        pipeline = IndexingPipeline(mock_embedding, mock_client, vector_store=mock_store)
        count = await pipeline.run(labels=["Concept"], batch_size=10)

        assert count == 2
        assert mock_store.upsert.await_count == 2

    @pytest.mark.asyncio
    async def test_run_returns_zero_for_empty_label(self):
        """Labels with no nodes contribute 0 to the count."""
        mock_client = MagicMock(spec=GraphClient)
        mock_client.execute = AsyncMock(return_value=[])

        mock_embedding = MagicMock(spec=BaseEmbeddingModel)
        pipeline = IndexingPipeline(mock_embedding, mock_client)
        count = await pipeline.run(labels=["EmptyLabel"])

        assert count == 0

    @pytest.mark.asyncio
    async def test_run_uses_default_labels_when_none(self):
        """When labels=None, pipeline uses default 8 concept labels."""
        mock_client = MagicMock(spec=GraphClient)
        mock_client.execute = AsyncMock(return_value=[])

        mock_embedding = MagicMock(spec=BaseEmbeddingModel)
        pipeline = IndexingPipeline(mock_embedding, mock_client)
        await pipeline.run()

        # Should have been called once per default label
        assert mock_client.execute.await_count == 8

    @pytest.mark.asyncio
    async def test_run_skips_upsert_when_no_vector_store(self):
        """When vector_store is None, embeddings are computed but not stored."""
        mock_client = MagicMock(spec=GraphClient)
        mock_client.execute = AsyncMock(return_value=[
            {"id": "node1", "name": "Test", "description": ""},
        ])

        mock_embedding = MagicMock(spec=BaseEmbeddingModel)
        mock_embedding.embed_batch = AsyncMock(return_value=[[0.1]])

        pipeline = IndexingPipeline(mock_embedding, mock_client, vector_store=None)
        count = await pipeline.run(labels=["Concept"])

        assert count == 1  # still counted as indexed
        mock_embedding.embed_batch.assert_awaited()  # embeddings computed
