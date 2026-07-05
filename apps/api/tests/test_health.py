"""Tests for API health endpoint."""

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
async def test_health_endpoint(client):
    """/health should return 200 with status ok or degraded."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ok", "degraded")
    assert "version" in data


@pytest.mark.asyncio
async def test_health_has_version(client):
    """/health should include version string."""
    response = await client.get("/api/v1/health")
    data = response.json()
    assert isinstance(data["version"], str)
    assert len(data["version"]) > 0
