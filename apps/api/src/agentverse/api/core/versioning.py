"""API versioning middleware — supports v1 and v2 via header or URL prefix."""

from fastapi import Request
from fastapi.responses import JSONResponse

from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

# Supported API versions
SUPPORTED_VERSIONS = {"v1"}
DEFAULT_VERSION = "v1"


def get_api_version(request: Request) -> str:
    """Extract API version from request.

    Priority:
    1. URL path prefix (/api/v2/...)
    2. X-API-Version header
    3. Accept-Version header
    4. Default (v1)
    """
    # Check URL path
    path = request.url.path
    if "/api/v2/" in path:
        return "v2"
    if "/api/v1/" in path:
        return "v1"

    # Check headers
    version = request.headers.get("X-API-Version", "")
    if not version:
        version = request.headers.get("Accept-Version", "")
    if version and version in SUPPORTED_VERSIONS:
        return version

    return DEFAULT_VERSION


async def versioning_middleware(request: Request, call_next) -> None:
    """Add API version info to response headers."""
    version = get_api_version(request)
    response = await call_next(request)
    response.headers["X-API-Version"] = version
    return response