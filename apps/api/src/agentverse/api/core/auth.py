"""API Key authentication middleware with production key validation."""

from fastapi import Request
from fastapi.responses import JSONResponse

from agentverse.api.core.key_management import authenticate_request
from agentverse.shared.config import Settings
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

# Endpoints that don't require authentication
PUBLIC_ENDPOINTS = {
    "/api/v1/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/metrics",
}


class APIKeyAuth:
    """API Key authentication handler."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or Settings()

    def is_public(self, path: str) -> bool:
        """Check if endpoint is public."""
        return path in PUBLIC_ENDPOINTS or path.startswith("/docs") or path.startswith("/redoc")

    def validate(self, request: Request) -> tuple[bool, str]:
        """Validate API key from request.

        Checks in order:
        1. Authorization: Bearer <key> header
        2. X-API-Key header

        Returns:
            (is_valid, role_or_error)
        """
        # Check Authorization header first
        auth_header = request.headers.get("Authorization", "")
        if auth_header:
            valid, result = authenticate_request(auth_header)
            if valid:
                return True, result

        # Fall back to X-API-Key header
        api_key = request.headers.get("X-API-Key", "")
        if api_key:
            valid, result = authenticate_request(f"Bearer {api_key}")
            if valid:
                return True, result

        if auth_header or api_key:
            logger.warning("Authentication failed", reason=result)
        return False, "Missing or invalid API key"


# Global auth handler
_auth: APIKeyAuth | None = None


def get_auth() -> APIKeyAuth:
    """Return the global auth handler."""
    global _auth
    if _auth is None:
        _auth = APIKeyAuth()
    return _auth