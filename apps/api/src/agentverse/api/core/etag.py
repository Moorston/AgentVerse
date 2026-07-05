"""ETag-based response caching middleware."""

import hashlib
import json
from typing import Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


def compute_etag(content: Any) -> str:
    """Compute ETag from response content."""
    if isinstance(content, (dict, list)):
        content_str = json.dumps(content, sort_keys=True)
    else:
        content_str = str(content)
    return hashlib.md5(content_str.encode()).hexdigest()


async def etag_middleware(request: Request, call_next: Any) -> Any:
    """Add ETag headers to GET responses for conditional caching."""
    response = await call_next(request)

    # Only for GET requests with JSON responses
    if request.method != "GET" or response.status_code != 200:
        return response

    # Read response body
    body = b""
    async for chunk in response.body_iterator:
        if isinstance(chunk, str):
            body += chunk.encode()
        else:
            body += chunk

    # Compute ETag
    etag = compute_etag(body.decode())

    # Check If-None-Match
    if_none_match = request.headers.get("If-None-Match", "")
    if if_none_match == etag:
        return Response(status_code=304)

    # Return response with ETag
    return JSONResponse(
        content=json.loads(body) if body else {},
        headers={
            "ETag": etag,
            "Cache-Control": "private, max-age=60",
        },
    )