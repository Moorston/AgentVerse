"""Tests for API versioning middleware."""

import pytest
from fastapi import Request
from starlette.testclient import TestClient

from agentverse.api.core.versioning import get_api_version, SUPPORTED_VERSIONS, DEFAULT_VERSION


class TestGetApiVersion:
    """Tests for get_api_version function."""

    def _make_request(self, path: str = "/api/v1/health", headers: dict | None = None) -> Request:
        """Create a mock request."""
        scope = {
            "type": "http",
            "method": "GET",
            "path": path,
            "headers": [],
        }
        if headers:
            for key, value in headers.items():
                scope["headers"].append((key.lower().encode(), value.encode()))
        return Request(scope)

    def test_default_version_from_url(self):
        request = self._make_request("/api/v1/concepts/")
        assert get_api_version(request) == "v1"

    def test_version_from_header(self):
        request = self._make_request("/other", {"X-API-Version": "v1"})
        assert get_api_version(request) == "v1"

    def test_version_from_accept_version_header(self):
        request = self._make_request("/other", {"Accept-Version": "v1"})
        assert get_api_version(request) == "v1"

    def test_default_version_fallback(self):
        request = self._make_request("/other")
        assert get_api_version(request) == DEFAULT_VERSION

    def test_unsupported_version_ignored(self):
        request = self._make_request("/other", {"X-API-Version": "v99"})
        assert get_api_version(request) == DEFAULT_VERSION

    def test_supported_versions_contains_v1(self):
        assert "v1" in SUPPORTED_VERSIONS


class TestVersioningMiddleware:
    """Tests for the versioning middleware integration."""

    def test_response_contains_version_header(self):
        from agentverse.api.main import app
        client = TestClient(app)
        response = client.get("/api/v1/health")
        assert "X-API-Version" in response.headers
        assert response.headers["X-API-Version"] == "v1"