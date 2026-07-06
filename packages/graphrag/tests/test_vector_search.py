"""Tests for VectorSearch — vector similarity search."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from agentverse.graphrag.embeddings.base import BaseEmbeddingModel
from agentverse.graphrag.retrieval.vector import VectorSearch


@pytest.fixture
def embedding_model():
    """Fixture: mock embedding model."""
    model = MagicMock(spec=BaseEmbeddingModel)
    model.embed = AsyncMock(return_value=[0.1, 0.2, 0.3])
    return model


@pytest.fixture
def mock_store():
    """Fixture: mock vector store."""
    store = MagicMock()
    store.search = AsyncMock(
        return_value=[
            {"id": "n1", "content": "result 1", "score": 0.95},
            {"id": "n2", "content": "result 2", "score": 0.85},
        ]
    )
    store.upsert = AsyncMock(return_value=None)
    return store


class TestVectorSearchEmptyStore:
    """Tests when store is None."""

    @pytest.mark.asyncio
    async def test_search_returns_empty_when_store_is_none(self, embedding_model):
        vs = VectorSearch(embedding_model, store=None)
        results = await vs.search("test query", top_k=10)
        assert results == []

    @pytest.mark.asyncio
    async def test_initialize_logs_warning_when_no_store(self, embedding_model):
        vs = VectorSearch(embedding_model, store=None)
        # Should not raise
        await vs.initialize()

    @pytest.mark.asyncio
    async def test_index_node_returns_embedding_even_without_store(self, embedding_model):
        vs = VectorSearch(embedding_model, store=None)
        embedding = await vs.index_node("n1", "some content")
        assert embedding == [0.1, 0.2, 0.3]


class TestVectorSearchWithStore:
    """Tests when store is provided."""

    @pytest.mark.asyncio
    async def test_search_delegates_to_store(self, embedding_model, mock_store):
        vs = VectorSearch(embedding_model, store=mock_store)
        results = await vs.search("test query", top_k=10)

        embedding_model.embed.assert_awaited_once_with("test query")
        mock_store.search.assert_awaited_once_with([0.1, 0.2, 0.3], top_k=10)
        assert len(results) == 2
        assert results[0]["id"] == "n1"
        assert results[1]["id"] == "n2"

    @pytest.mark.asyncio
    async def test_index_node_delegates_to_store_upsert(self, embedding_model, mock_store):
        vs = VectorSearch(embedding_model, store=mock_store)
        embedding = await vs.index_node("n1", "some content", label="Concept")

        embedding_model.embed.assert_awaited_once_with("some content")
        mock_store.upsert.assert_awaited_once_with(
            "n1", [0.1, 0.2, 0.3], "some content", metadata={"label": "Concept"}
        )
        assert embedding == [0.1, 0.2, 0.3]

    @pytest.mark.asyncio
    async def test_initialize_logs_info_when_store_present(self, embedding_model, mock_store):
        vs = VectorSearch(embedding_model, store=mock_store)
        # Should not raise
        await vs.initialize()

    @pytest.mark.asyncio
    async def test_search_passes_top_k_to_store(self, embedding_model, mock_store):
        vs = VectorSearch(embedding_model, store=mock_store)
        await vs.search("query", top_k=5)
        mock_store.search.assert_awaited_once_with([0.1, 0.2, 0.3], top_k=5)