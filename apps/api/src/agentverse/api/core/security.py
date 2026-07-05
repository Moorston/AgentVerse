"""Security utilities — input validation and sanitization."""

import re
from typing import Any

from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

# Patterns that indicate potential injection attacks
CYPHER_INJECTION_PATTERNS = [
    r";\s*(MATCH|CREATE|DELETE|DETACH|MERGE|SET|REMOVE|DROP)",  # Cypher statement injection
    r"//",  # Comment injection
    r"/\*.*\*/",  # Block comment injection
    r"--\s",  # Line comment injection
]

XSS_PATTERNS = [
    r"<script[^>]*>",  # Script tags
    r"javascript:",  # JavaScript protocol
    r"on\w+\s*=",  # Event handlers
    r"<iframe",  # Iframe injection
]


def sanitize_name(name: str) -> str:
    """Sanitize a concept/node name.

    Rules:
    - Strip whitespace
    - Remove control characters
    - Limit length to 500 characters
    - Remove potential injection patterns
    """
    if not name:
        return ""

    # Strip whitespace
    name = name.strip()

    # Remove control characters
    name = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", name)

    # Limit length
    name = name[:500]

    return name


def validate_name(name: str) -> tuple[bool, str]:
    """Validate a concept/node name.

    Returns:
        (is_valid, error_message)
    """
    if not name:
        return False, "Name cannot be empty"

    if len(name) > 500:
        return False, "Name too long (max 500 characters)"

    # Check for Cypher injection
    for pattern in CYPHER_INJECTION_PATTERNS:
        if re.search(pattern, name, re.IGNORECASE):
            logger.warning("Potential Cypher injection detected", name=name[:100])
            return False, "Invalid characters in name"

    return True, ""


def validate_query(query: str) -> tuple[bool, str]:
    """Validate a search query string.

    Returns:
        (is_valid, error_message)
    """
    if not query:
        return True, ""  # Empty query is valid (returns empty results)

    if len(query) > 1000:
        return False, "Query too long (max 1000 characters)"

    # Check for XSS
    for pattern in XSS_PATTERNS:
        if re.search(pattern, query, re.IGNORECASE):
            logger.warning("Potential XSS detected in query", query=query[:100])
            return False, "Invalid characters in query"

    return True, ""


def sanitize_properties(properties: dict[str, Any]) -> dict[str, Any]:
    """Sanitize all string values in a properties dict."""
    sanitized = {}
    for key, value in properties.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_name(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_name(v) if isinstance(v, str) else v for v in value]
        else:
            sanitized[key] = value
    return sanitized