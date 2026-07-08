"""Tests for API endpoints with mocked Neo4j."""

import pytest
from httpx import AsyncClient, ASGITransport

# Dev API key pre-loaded by key_management.py
DEV_API_KEY = "av-dev-key"
AUTH_HEADERS = {"Authorization": f"Bearer {DEV_API_KEY}"}


@pytest.mark.asyncio
async def test_health_endpoint(app_with_mock):
    """Test health check endpoint returns 200 (public — no auth needed)."""
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_concepts_list_endpoint(app_with_mock):
    """Test concepts list endpoint returns 200 with auth."""
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/concepts/", headers=AUTH_HEADERS)
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_endpoint(app_with_mock):
    """Test search endpoint returns 200 with auth."""
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/search/?q=test", headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "results" in data


@pytest.mark.asyncio
async def test_concepts_pagination(app_with_mock):
    """Test concepts endpoint with pagination and auth."""
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/concepts/?page=1&size=10", headers=AUTH_HEADERS)
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_concepts_without_auth(app_with_mock):
    """Test concepts endpoint returns 401 without auth."""
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/concepts/")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_health_without_auth(app_with_mock):
    """Test health endpoint is public — no auth required."""
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200