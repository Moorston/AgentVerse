"""Tests for API search endpoint."""

import pytest
from httpx import AsyncClient, ASGITransport

from agentverse.api.main import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_search_endpoint(client):
    """/search/ should return 200."""
    response = await client.get("/api/v1/search/", params={"q": "ReAct"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_returns_results(client):
    """/search/ should return a dict with results."""
    response = await client.get("/api/v1/search/", params={"q": "agent"})
    data = response.json()
    assert isinstance(data, dict)
    assert "results" in data
    assert isinstance(data["results"], list)
