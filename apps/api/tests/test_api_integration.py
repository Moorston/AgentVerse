"""Tests for API integration — end-to-end endpoint testing."""

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
async def test_timeline_endpoint(client):
    """/concepts/timeline/{name} should return 200."""
    response = await client.get("/api/v1/concepts/timeline/ReAct")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_connections_endpoint(client):
    """/concepts/connections/{name} should return 200."""
    response = await client.get("/api/v1/concepts/connections/ReAct")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_endpoint(client):
    """/search/ should return 200."""
    response = await client.get("/api/v1/search/", params={"q": "agent"})
    assert response.status_code == 200
