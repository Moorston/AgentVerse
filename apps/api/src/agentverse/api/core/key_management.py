"""API key generation and validation for production security."""

import hashlib
import hmac
import secrets
import time
from typing import Any

from agentverse.shared.config import Settings
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

# In-memory API key store (in production, use a database or external secrets manager)
_api_keys: dict[str, dict[str, Any]] = {}

# Default keys for development
if Settings().environment == "development":
    _api_keys["av-dev-key"] = {
        "name": "Development Key",
        "role": "admin",
        "active": True,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "last_used": None,
        "usage_count": 0,
    }


def generate_api_key(name: str = "", role: str = "user") -> str:
    """Generate a new API key.

    Args:
        name: Human-readable name for the key.
        role: Access role ('admin', 'user', 'readonly').

    Returns:
        The generated API key string.
    """
    key = f"av_{secrets.token_urlsafe(32)}"
    _api_keys[key] = {
        "name": name or f"Key-{time.strftime('%Y%m%d-%H%M%S')}",
        "role": role,
        "active": True,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "last_used": None,
        "usage_count": 0,
    }
    logger.info("API key generated", key_name=_api_keys[key]["name"], role=role)
    return key


def validate_api_key(key: str) -> tuple[bool, str]:
    """Validate an API key.

    Args:
        key: The API key to validate.

    Returns:
        (is_valid, role_or_error)
    """
    if not key:
        return False, "Missing API key"

    key_info = _api_keys.get(key)
    if not key_info:
        return False, "Invalid API key"

    if not key_info.get("active", False):
        return False, "API key is deactivated"

    # Update usage stats
    key_info["last_used"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    key_info["usage_count"] += 1

    return True, key_info.get("role", "user")


def revoke_api_key(key: str) -> bool:
    """Revoke/delete an API key.

    Args:
        key: The API key to revoke.

    Returns:
        True if the key was found and revoked.
    """
    if key not in _api_keys:
        return False
    _api_keys[key]["active"] = False
    logger.info("API key revoked", key_name=_api_keys[key]["name"])
    return True


def list_api_keys() -> list[dict[str, Any]]:
    """List all API keys (without exposing the keys themselves)."""
    return [
        {
            "name": info["name"],
            "role": info["role"],
            "active": info["active"],
            "created_at": info["created_at"],
            "last_used": info.get("last_used"),
            "usage_count": info.get("usage_count", 0),
        }
        for key, info in _api_keys.items()
    ]


def authenticate_request(auth_header: str) -> tuple[bool, str]:
    """Authenticate a request using the Authorization header.

    Args:
        auth_header: The value of the Authorization header.

    Returns:
        (is_authenticated, role)
    """
    if not auth_header:
        return False, ""

    key = auth_header
    if auth_header.startswith("Bearer "):
        key = auth_header[7:]

    return validate_api_key(key)