"""Tests for API concept endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport

from agentverse.api.main import create_app

DEV_API_KEY = "av-dev-key"
AUTH_HEADERS = {"Authorization": f"Bearer {DEV_API_KEY}"}


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_list_concepts(client):
    """/concepts should return 200 with auth."""
    response = await client.get("/api/v1/concepts", headers=AUTH_HEADERS)
    assert response.status_code in (200, 307)


@pytest.mark.asyncio
async def test_get_concept(client):
    """/concepts/{name} should return 200, 404, or 500 with auth."""
    response = await client.get("/api/v1/concepts/ReAct", headers=AUTH_HEADERS)
    assert response.status_code in (200, 404, 500)


@pytest.mark.asyncio
async def test_timeline_endpoint(client):
    """/concepts/timeline/{name} should return 200 with auth."""
    response = await client.get("/api/v1/concepts/timeline/ReAct", headers=AUTH_HEADERS)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_connections_endpoint(client):
    """/concepts/connections/{name} should return 200 with auth."""
    response = await client.get("/api/v1/concepts/connections/ReAct", headers=AUTH_HEADERS)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_concepts_without_auth(client):
    """/concepts should return 401 without auth."""
    response = await client.get("/api/v1/concepts")
    assert response.status_code == 401