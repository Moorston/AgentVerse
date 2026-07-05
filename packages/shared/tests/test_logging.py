"""Tests for shared logging module."""

from agentverse.shared.logging import get_logger, bind_request_context, clear_request_context


def test_get_logger_returns_logger():
    """get_logger should return a structlog BoundLogger."""
    logger = get_logger("test")
    assert logger is not None
    assert hasattr(logger, "info")
    assert hasattr(logger, "warning")


def test_get_logger_default_name():
    """get_logger with no name should still work."""
    logger = get_logger()
    assert logger is not None


def test_bind_and_clear_request_context():
    """Request context binding should not raise."""
    bind_request_context(request_id="test-123")
    clear_request_context()  # Should not raise
