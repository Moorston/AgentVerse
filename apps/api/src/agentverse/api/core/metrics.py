"""Prometheus-compatible metrics collection and recording."""

import time
from collections import defaultdict

# Metrics storage
_request_count: dict[str, int] = defaultdict(int)
_request_duration_sum: dict[str, float] = defaultdict(float)
_request_duration_count: dict[str, int] = defaultdict(int)
_error_count: dict[str, int] = defaultdict(int)
_active_connections = 0

_start_time = time.monotonic()


def record_request(endpoint: str, duration_ms: float, status_code: int) -> None:
    """Record a request metric."""
    _request_count[endpoint] += 1
    _request_duration_sum[endpoint] += duration_ms
    _request_duration_count[endpoint] += 1
    if status_code >= 400:
        _error_count[endpoint] += 1


def set_active_connections(count: int) -> None:
    """Update active connection count."""
    global _active_connections
    _active_connections = count


def get_metrics_text() -> str:
    """Return Prometheus-compatible metrics text."""
    lines: list[str] = []
    uptime = time.monotonic() - _start_time

    # Uptime
    lines.append("# HELP agentverse_uptime_seconds Service uptime in seconds")
    lines.append("# TYPE agentverse_uptime_seconds gauge")
    lines.append(f"agentverse_uptime_seconds {uptime:.2f}")

    # Active connections
    lines.append("# HELP agentverse_active_connections Current active connections")
    lines.append("# TYPE agentverse_active_connections gauge")
    lines.append(f"agentverse_active_connections {_active_connections}")

    # Request count
    lines.append("# HELP agentverse_requests_total Total requests by endpoint")
    lines.append("# TYPE agentverse_requests_total counter")
    for endpoint, count in sorted(_request_count.items()):
        lines.append(f'agentverse_requests_total{{endpoint="{endpoint}"}} {count}')

    # Request duration
    lines.append("# HELP agentverse_request_duration_ms_avg Average request duration in ms")
    lines.append("# TYPE agentverse_request_duration_ms_avg gauge")
    for endpoint in sorted(_request_duration_sum.keys()):
        total = _request_duration_sum[endpoint]
        count = _request_duration_count[endpoint]
        avg = total / count if count > 0 else 0
        lines.append(f'agentverse_request_duration_ms_avg{{endpoint="{endpoint}"}} {avg:.2f}')

    # Error count
    lines.append("# HELP agentverse_errors_total Total errors by endpoint")
    lines.append("# TYPE agentverse_errors_total counter")
    for endpoint, count in sorted(_error_count.items()):
        lines.append(f'agentverse_errors_total{{endpoint="{endpoint}"}} {count}')

    return "\n".join(lines) + "\n"