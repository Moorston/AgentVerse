"""Tests for API authentication with key management."""

from agentverse.api.core.auth import APIKeyAuth, get_auth
from agentverse.api.core.key_management import generate_api_key, revoke_api_key
from agentverse.shared.config import Settings


class MockRequest:
    """Mock FastAPI Request for testing."""
    def __init__(self, headers: dict[str, str] | None = None, path: str = "/test") -> None:
        self.headers = headers or {}
        self.client = type("Client", (), {"host": "127.0.0.1"})()
        self.url = type("URL", (), {"path": path})()


def test_auth_development_mode():
    """Test that auth is disabled in development mode."""
    settings = Settings(environment="development")
    auth = APIKeyAuth(settings)
    request = MockRequest()
    valid, msg = auth.validate(request)
    assert valid is True
    assert msg == ""


def test_auth_public_endpoints():
    """Test that public endpoints are recognized."""
    auth = APIKeyAuth()
    assert auth.is_public("/api/v1/health") is True
    assert auth.is_public("/docs") is True
    assert auth.is_public("/redoc") is True
    assert auth.is_public("/openapi.json") is True
    assert auth.is_public("/api/v1/concepts") is False


def test_auth_bearer_token():
    """Test Bearer token authentication with valid key."""
    settings = Settings(environment="production")
    auth = APIKeyAuth(settings)
    valid_key = generate_api_key(name="test-key")
    request = MockRequest(headers={"Authorization": f"Bearer {valid_key}"})
    valid, msg = auth.validate(request)
    assert valid is True


def test_auth_api_key_header():
    """Test X-API-Key header authentication."""
    settings = Settings(environment="production")
    auth = APIKeyAuth(settings)
    valid_key = generate_api_key(name="test-key-2")
    request = MockRequest(headers={"X-API-Key": valid_key})
    valid, msg = auth.validate(request)
    assert valid is True


def test_auth_missing_key_production():
    """Test that missing key fails in production."""
    settings = Settings(environment="production")
    auth = APIKeyAuth(settings)
    request = MockRequest()
    valid, msg = auth.validate(request)
    assert valid is False
    assert "Missing" in msg


def test_auth_invalid_key_production():
    """Test that invalid key fails in production."""
    settings = Settings(environment="production")
    auth = APIKeyAuth(settings)
    request = MockRequest(headers={"Authorization": "Bearer invalid-key-123"})
    valid, msg = auth.validate(request)
    assert valid is False