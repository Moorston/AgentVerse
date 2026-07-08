"""Tests for export and batch API endpoints.

Tests at the public seam: HTTP request -> HTTP response.
Repository is mocked via conftest fixtures; behavior is verified through status codes and response bodies.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from agentverse.api.core.context import get_context, AppContext
from agentverse.api.core.dependencies import get_repository

DEV_API_KEY = "av-dev-key"
AUTH_HEADERS = {"Authorization": f"Bearer {DEV_API_KEY}"}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def app_with_repo_override(app_with_mock, mock_repo):
    """Extend app_with_mock to also override get_repository directly."""
    app_with_mock.dependency_overrides[get_repository] = lambda: mock_repo
    yield app_with_mock
    app_with_mock.dependency_overrides.pop(get_repository, None)


# ---------------------------------------------------------------------------
# Export endpoints
# ---------------------------------------------------------------------------


class TestExportJSON:
    """Tests for GET /api/v1/export/json."""

    @pytest.mark.asyncio
    async def test_export_json_returns_nodes_and_edges(self, app_with_repo_override, mock_repo):
        """Export JSON returns nodes, edges, and metadata."""
        mock_repo.set_raw_result("match (n)", [
            {"n": {"name": "ReAct", "labels": ["Concept"], "category": "reasoning"}},
        ])
        mock_repo.set_raw_result("match (a)-[r]->(b)", [
            {"source": "ReAct", "target": "ToolCalling", "rel_type": "PROPOSES"},
        ])

        transport = ASGITransport(app=app_with_repo_override)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/export/json", headers=AUTH_HEADERS)

        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) == 1
        assert data["nodes"][0]["id"] == "ReAct"
        assert len(data["edges"]) == 1
        assert data["edges"][0]["type"] == "PROPOSES"
        assert data["metadata"]["node_count"] == 1

    @pytest.mark.asyncio
    async def test_export_json_respects_limit(self, app_with_repo_override, mock_repo):
        """Export JSON passes limit parameter to the query."""
        mock_repo.set_raw_result("match (n)", [])

        transport = ASGITransport(app=app_with_repo_override)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/export/json", params={"limit": 50}, headers=AUTH_HEADERS)

        assert resp.status_code == 200
        assert resp.json()["metadata"]["node_count"] == 0


class TestExportCSV:
    """Tests for GET /api/v1/export/csv."""

    @pytest.mark.asyncio
    async def test_export_csv_returns_csv_content(self, app_with_repo_override, mock_repo):
        """Export CSV returns text/csv with header row."""
        mock_repo.set_raw_result("match (n)", [
            {"name": "ReAct", "description": "Reasoning+Acting", "labels": ["Concept"]},
        ])

        transport = ASGITransport(app=app_with_repo_override)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/export/csv", headers=AUTH_HEADERS)

        assert resp.status_code == 200
        assert resp.headers["content-type"] == "text/csv; charset=utf-8"
        lines = resp.text.strip().replace("\r", "").split("\n")
        assert lines[0] == "name,description,labels"
        assert "ReAct" in lines[1]

    @pytest.mark.asyncio
    async def test_export_csv_empty_graph(self, app_with_repo_override, mock_repo):
        """Export CSV on empty graph returns only header row."""
        mock_repo.set_raw_result("match (n)", [])

        transport = ASGITransport(app=app_with_repo_override)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/export/csv", headers=AUTH_HEADERS)

        assert resp.status_code == 200
        lines = resp.text.strip().split("\n")
        assert len(lines) == 1  # header only


# ---------------------------------------------------------------------------
# Batch endpoints
# ---------------------------------------------------------------------------


class TestBatchCreateConcepts:
    """Tests for POST /api/v1/batch/concepts."""

    @pytest.mark.asyncio
    async def test_batch_create_concepts(self, app_with_repo_override, mock_repo):
        """Batch create creates multiple concepts in one request."""
        transport = ASGITransport(app=app_with_repo_override)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/v1/batch/concepts", headers=AUTH_HEADERS, json={
                "concepts": [
                    {"name": "ReAct", "description": "Reasoning+Acting", "category": "reasoning"},
                    {"name": "ChainOfThought", "description": "Step-by-step", "category": "reasoning"},
                ],
            })

        assert resp.status_code == 200
        data = resp.json()
        assert data["created"] == 2
        assert data["errors"] == 0

    @pytest.mark.asyncio
    async def test_batch_create_skips_concepts_without_name(self, app_with_repo_override, mock_repo):
        """Concepts missing 'name' are counted as errors."""
        transport = ASGITransport(app=app_with_repo_override)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/v1/batch/concepts", headers=AUTH_HEADERS, json={
                "concepts": [
                    {"name": "ReAct"},
                    {"description": "no name field"},
                ],
            })

        assert resp.status_code == 200
        data = resp.json()
        assert data["created"] == 1
        assert data["errors"] == 1

    @pytest.mark.asyncio
    async def test_batch_create_empty_list(self, app_with_repo_override, mock_repo):
        """Empty list yields 0 created, 0 errors."""
        transport = ASGITransport(app=app_with_repo_override)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/v1/batch/concepts", headers=AUTH_HEADERS, json={"concepts": []})

        assert resp.status_code == 200
        assert resp.json()["created"] == 0
        assert resp.json()["errors"] == 0


class TestBatchCreateRelationships:
    """Tests for POST /api/v1/batch/relationships."""

    @pytest.mark.asyncio
    async def test_batch_create_relationships(self, app_with_repo_override, mock_repo):
        """Batch create relationships in one request."""
        transport = ASGITransport(app=app_with_repo_override)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/v1/batch/relationships", headers=AUTH_HEADERS, json={
                "relationships": [
                    {"source": "ReAct", "target": "ChainOfThought", "type": "EXTENDS"},
                    {"source": "ReAct", "target": "ToolCalling", "type": "PROPOSES"},
                ],
            })

        assert resp.status_code == 200
        data = resp.json()
        assert data["created"] == 2
        assert data["errors"] == 0

    @pytest.mark.asyncio
    async def test_batch_create_skips_relationships_without_source(self, app_with_repo_override, mock_repo):
        """Relationships missing source or target are counted as errors."""
        transport = ASGITransport(app=app_with_repo_override)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/v1/batch/relationships", headers=AUTH_HEADERS, json={
                "relationships": [
                    {"source": "ReAct", "target": "ChainOfThought", "type": "EXTENDS"},
                    {"target": "ChainOfThought", "type": "RELATED_TO"},
                ],
            })

        assert resp.status_code == 200
        data = resp.json()
        assert data["created"] == 1
        assert data["errors"] == 1


class TestBatchDeleteConcepts:
    """Tests for DELETE /api/v1/batch/concepts."""

    @pytest.mark.asyncio
    async def test_batch_delete_existing_concepts(self, app_with_repo_override, mock_repo):
        """Batch delete removes existing concepts, returns deleted count."""
        mock_repo._nodes["ReAct"] = {"name": "ReAct"}
        mock_repo._nodes["ChainOfThought"] = {"name": "ChainOfThought"}

        transport = ASGITransport(app=app_with_repo_override)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.request(
                "DELETE",
                "/api/v1/batch/concepts",
                headers=AUTH_HEADERS,
                json=["ReAct", "ChainOfThought"],
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["deleted"] == 2
        assert data["errors"] == 0

    @pytest.mark.asyncio
    async def test_batch_delete_nonexistent_concepts(self, app_with_repo_override, mock_repo):
        """Deleting nonexistent concepts still counts as success (no exception)."""
        transport = ASGITransport(app=app_with_repo_override)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.request(
                "DELETE",
                "/api/v1/batch/concepts",
                headers=AUTH_HEADERS,
                json=["NonExistent"],
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["deleted"] == 1
        assert data["errors"] == 0