"""Tests for Prometheus metrics collection."""

import pytest

from agentverse.api.core.metrics import (
    record_request,
    set_active_connections,
    get_metrics_text,
)


class TestRecordRequest:
    """Tests for record_request function."""

    def setup_method(self):
        """Reset global state before each test."""
        from agentverse.api.core.metrics import _request_count, _request_duration_sum, _request_duration_count, _error_count
        _request_count.clear()
        _request_duration_sum.clear()
        _request_duration_count.clear()
        _error_count.clear()

    def test_records_single_request(self):
        record_request("/api/v1/concepts/", 15.5, 200)
        text = get_metrics_text()
        assert '/api/v1/concepts/' in text
        assert 'agentverse_requests_total{endpoint="/api/v1/concepts/"} 1' in text

    def test_accumulates_requests(self):
        record_request("/api/v1/health", 5.0, 200)
        record_request("/api/v1/health", 10.0, 200)
        record_request("/api/v1/health", 8.0, 200)
        text = get_metrics_text()
        assert 'agentverse_requests_total{endpoint="/api/v1/health"} 3' in text

    def test_records_errors(self):
        record_request("/api/v1/concepts/", 10.0, 404)
        record_request("/api/v1/concepts/", 12.0, 200)
        text = get_metrics_text()
        assert 'agentverse_errors_total{endpoint="/api/v1/concepts/"} 1' in text

    def test_calculates_average_duration(self):
        record_request("/test", 10.0, 200)
        record_request("/test", 20.0, 200)
        text = get_metrics_text()
        assert 'agentverse_request_duration_ms_avg{endpoint="/test"} 15.00' in text


class TestSetActiveConnections:
    """Tests for set_active_connections function."""

    def test_sets_connection_count(self):
        set_active_connections(5)
        text = get_metrics_text()
        assert 'agentverse_active_connections 5' in text

    def test_updates_connection_count(self):
        set_active_connections(10)
        text = get_metrics_text()
        assert 'agentverse_active_connections 10' in text


class TestGetMetricsText:
    """Tests for get_metrics_text output format."""

    def setup_method(self):
        from agentverse.api.core.metrics import _request_count, _request_duration_sum, _request_duration_count, _error_count
        _request_count.clear()
        _request_duration_sum.clear()
        _request_duration_count.clear()
        _error_count.clear()

    def test_contains_help_and_type_lines(self):
        text = get_metrics_text()
        assert '# HELP agentverse_uptime_seconds' in text
        assert '# TYPE agentverse_uptime_seconds gauge' in text
        assert '# HELP agentverse_requests_total' in text
        assert '# TYPE agentverse_requests_total counter' in text

    def test_uptime_is_positive(self):
        text = get_metrics_text()
        for line in text.split('\n'):
            if line.startswith('agentverse_uptime_seconds '):
                value = float(line.split(' ')[1])
                assert value >= 0
                break

    def test_empty_metrics_still_has_headers(self):
        text = get_metrics_text()
        assert 'agentverse_uptime_seconds' in text
        assert 'agentverse_active_connections' in text