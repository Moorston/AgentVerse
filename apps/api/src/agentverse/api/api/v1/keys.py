"""API key management endpoints — admin-only operations."""

from fastapi import APIRouter, HTTPException, Request

from agentverse.api.core.key_management import (
    generate_api_key,
    revoke_api_key,
    list_api_keys,
)
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


def _require_admin(request: Request) -> None:
    """Check that the authenticated user has admin role."""
    role = getattr(request.state, "auth_role", "")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")


@router.post("/keys")
async def create_api_key(
    request: Request,
    name: str = "",
    role: str = "user",
) -> dict:
    """Generate a new API key. Admin role required."""
    _require_admin(request)
    key = generate_api_key(name=name, role=role)
    return {"key": key, "name": name, "role": role}


@router.delete("/keys/{key}")
async def delete_api_key(
    request: Request,
    key: str,
) -> dict:
    """Revoke an API key. Admin role required."""
    _require_admin(request)
    if revoke_api_key(key):
        return {"status": "revoked"}
    raise HTTPException(status_code=404, detail="Key not found")


@router.get("/keys")
async def get_api_keys(
    request: Request,
) -> list[dict]:
    """List all API keys (without exposing the keys themselves). Admin role required."""
    _require_admin(request)
    return list_api_keys()