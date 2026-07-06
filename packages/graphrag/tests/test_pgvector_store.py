"""Tests for PgVectorStore — pgvector-backed vector storage."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agentverse.graphrag.retrieval.pgvector_store import PgVectorStore


@pytest.fixture
def mock_conn():
    """Fixture: mock asyncpg connection."""
    conn = AsyncMock()
    return conn


@pytest.fixture
def store():
    """Fixture: PgVectorStore instance with DSN."""
    return PgVectorStore(dsn="postgresql://user:pass@localhost/testdb", vector_dim=3)


@pytest.fixture
def connected_store(store, mock_conn):
    """Fixture: PgVectorStore with a connected mock pool."""
    # Create an async context manager for pool.acquire()
    acquire_cm = MagicMock()
    acquire_cm.__aenter__ = AsyncMock(return_value=mock_conn)
    acquire_cm.__aexit__ = AsyncMock(return_value=None)

    mock_pool = MagicMock()
    mock_pool.acquire = MagicMock(return_value=acquire_cm)

    with patch.object(store, "_pool", mock_pool):
        yield store


class TestPgVectorStoreUpsert:
    """Tests for upsert method."""

    @pytest.mark.asyncio
    async def test_upsert_inserts_new_row(self, connected_store, mock_conn):
        await connected_store.upsert("n1", [0.1, 0.2, 0.3], "test content", {"label": "Concept"})

        mock_conn.execute.assert_awaited_once()
        call_args = mock_conn.execute.call_args
        sql = call_args[0][0]
        params = call_args[0][1:]
        assert "$1" in sql or "INSERT INTO" in sql
        assert "ON CONFLICT" in sql
        assert params[0] == "n1"
        assert params[1] == [0.1, 0.2, 0.3]
        assert params[2] == "test content"
        assert params[3] == {"label": "Concept"}

    @pytest.mark.asyncio
    async def test_upsert_without_metadata(self, connected_store, mock_conn):
        await connected_store.upsert("n2", [0.4, 0.5, 0.6])

        call_args = mock_conn.execute.call_args
        params = call_args[0][1:]
        assert params[0] == "n2"
        assert params[3] == {}  # empty dict as default


class TestPgVectorStoreDelete:
    """Tests for delete method."""

    @pytest.mark.asyncio
    async def test_delete_single_id(self, connected_store, mock_conn):
        mock_conn.execute = AsyncMock(return_value="DELETE 1")

        count = await connected_store.delete("n1")

        assert count == 1
        mock_conn.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_multiple_ids(self, connected_store, mock_conn):
        mock_conn.execute = AsyncMock(return_value="DELETE 3")

        count = await connected_store.delete("n1", "n2", "n3")

        assert count == 3

    @pytest.mark.asyncio
    async def test_delete_returns_zero_on_empty_result(self, connected_store, mock_conn):
        mock_conn.execute = AsyncMock(return_value="DELETE 0")

        count = await connected_store.delete("nonexistent")
        assert count == 0


class TestPgVectorStoreCount:
    """Tests for count method."""

    @pytest.mark.asyncio
    async def test_count_returns_row_count(self, connected_store, mock_conn):
        mock_conn.fetchval = AsyncMock(return_value=5)

        count = await connected_store.count()
        assert count == 5

    @pytest.mark.asyncio
    async def test_count_zero_when_empty(self, connected_store, mock_conn):
        mock_conn.fetchval = AsyncMock(return_value=0)

        count = await connected_store.count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_count_none_becomes_zero(self, connected_store, mock_conn):
        mock_conn.fetchval = AsyncMock(return_value=None)

        count = await connected_store.count()
        assert count == 0


class TestPgVectorStoreSearch:
    """Tests for search method."""

    @pytest.mark.asyncio
    async def test_search_returns_results(self, connected_store, mock_conn):
        mock_conn.fetch = AsyncMock(
            return_value=[
                {
                    "id": "n1",
                    "content": "result 1",
                    "metadata": {"label": "Concept"},
                    "created_at": None,
                    "similarity": 0.95,
                },
                {
                    "id": "n2",
                    "content": "result 2",
                    "metadata": {},
                    "created_at": None,
                    "similarity": 0.85,
                },
            ]
        )

        results = await connected_store.search([0.1, 0.2, 0.3], top_k=2)

        assert len(results) == 2
        assert results[0]["id"] == "n1"
        assert results[0]["score"] == 0.95
        assert results[1]["id"] == "n2"
        assert results[1]["score"] == 0.85

    @pytest.mark.asyncio
    async def test_search_with_metadata_filter(self, connected_store, mock_conn):
        mock_conn.fetch = AsyncMock(return_value=[])

        await connected_store.search(
            [0.1, 0.2, 0.3],
            top_k=5,
            metadata_filter={"label": "Paper"},
        )

        call_args = mock_conn.fetch.call_args
        params = call_args[0][1:]
        assert len(params) == 4  # embedding, top_k, offset, metadata_filter

    @pytest.mark.asyncio
    async def test_search_with_offset(self, connected_store, mock_conn):
        mock_conn.fetch = AsyncMock(return_value=[])

        await connected_store.search([0.1, 0.2, 0.3], top_k=5, offset=10)

        call_args = mock_conn.fetch.call_args
        params = call_args[0][1:]
        # params: [query_embedding, top_k, offset]
        assert params[1] == 5
        assert params[2] == 10

    @pytest.mark.asyncio
    async def test_search_empty_results(self, connected_store, mock_conn):
        mock_conn.fetch = AsyncMock(return_value=[])

        results = await connected_store.search([0.1, 0.2, 0.3], top_k=10)
        assert results == []