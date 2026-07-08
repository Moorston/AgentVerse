"""Tests for shared utility functions."""

import pytest

from agentverse.shared.utils.text import truncate, slugify
from agentverse.shared.utils.retry import retry


def test_truncate_short_text():
    """Short text should pass through unchanged."""
    assert truncate("hello", max_length=100) == "hello"


def test_truncate_long_text():
    """Long text should be truncated with ellipsis."""
    result = truncate("a" * 2000, max_length=100)
    assert len(result) <= 103  # 100 + "..."
    assert result.endswith("...")


def test_slugify_basic():
    """slugify should lowercase and replace spaces."""
    assert slugify("Hello World") == "hello-world"


def test_slugify_slashes():
    """slugify should replace slashes."""
    assert slugify("a/b/c") == "a-b-c"


@pytest.mark.asyncio
async def test_retry_success():
    """Retry decorator should return result on success."""
    call_count = 0

    @retry(max_attempts=3, delay=0.01)
    async def success_func():
        nonlocal call_count
        call_count += 1
        return "ok"

    result = await success_func()
    assert result == "ok"
    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_exhaustion():
    """Retry decorator should raise after max attempts."""
    @retry(max_attempts=2, delay=0.01)
    async def fail_func():
        raise ValueError("always fails")

    with pytest.raises(ValueError):
        await fail_func()
