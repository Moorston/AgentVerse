#!/usr/bin/env python3
"""Performance benchmark — measure API response times and throughput.

Usage:
    python scripts/benchmark.py                # Run all benchmarks
    python scripts/benchmark.py --endpoint /api/v1/health  # Benchmark specific endpoint
"""

import argparse
import asyncio
import statistics
import time
from typing import Any

import httpx


BASE_URL = "http://localhost:8000"
ENDPOINTS = [
    "/api/v1/health",
    "/api/v1/concepts/?size=10",
    "/api/v1/search/?q=ReAct&strategy=graph",
    "/api/v1/frameworks/?size=10",
    "/api/v1/export/json?limit=100",
]


async def benchmark_endpoint(
    url: str,
    num_requests: int = 50,
    concurrency: int = 10,
) -> dict[str, Any]:
    """Benchmark a single endpoint.

    Args:
        url: Full URL to benchmark.
        num_requests: Total number of requests.
        concurrency: Number of concurrent requests.

    Returns:
        Benchmark results with timing statistics.
    """
    semaphore = asyncio.Semaphore(concurrency)
    latencies: list[float] = []
    errors = 0

    async def make_request(client: httpx.AsyncClient) -> None:
        nonlocal errors
        async with semaphore:
            start = time.monotonic()
            try:
                response = await client.get(url)
                elapsed = (time.monotonic() - start) * 1000
                latencies.append(elapsed)
                if response.status_code >= 400:
                    errors += 1
            except Exception:
                errors += 1

    async with httpx.AsyncClient(timeout=30) as client:
        start_time = time.monotonic()
        await asyncio.gather(*[make_request(client) for _ in range(num_requests)])
        total_time = time.monotonic() - start_time

    if not latencies:
        return {"url": url, "error": "All requests failed"}

    return {
        "url": url,
        "requests": num_requests,
        "concurrency": concurrency,
        "total_time_ms": round(total_time * 1000, 2),
        "requests_per_second": round(num_requests / total_time, 2),
        "errors": errors,
        "latency": {
            "min_ms": round(min(latencies), 2),
            "max_ms": round(max(latencies), 2),
            "avg_ms": round(statistics.mean(latencies), 2),
            "median_ms": round(statistics.median(latencies), 2),
            "p95_ms": round(sorted(latencies)[int(len(latencies) * 0.95)], 2),
            "p99_ms": round(sorted(latencies)[int(len(latencies) * 0.99)], 2),
        },
    }


async def run_benchmarks(
    endpoints: list[str],
    num_requests: int = 50,
    concurrency: int = 10,
) -> list[dict[str, Any]]:
    """Run benchmarks on multiple endpoints."""
    results = []
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"\nBenchmarking: {endpoint}")
        result = await benchmark_endpoint(url, num_requests, concurrency)
        results.append(result)
        print(f"  Avg: {result.get('latency', {}).get('avg_ms', 'N/A')}ms | "
              f"P95: {result.get('latency', {}).get('p95_ms', 'N/A')}ms | "
              f"RPS: {result.get('requests_per_second', 'N/A')} | "
              f"Errors: {result.get('errors', 0)}")
    return results


async def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="AgentVerse performance benchmark")
    parser.add_argument("--endpoint", type=str, help="Specific endpoint to benchmark")
    parser.add_argument("--requests", type=int, default=50, help="Number of requests")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent requests")
    args = parser.parse_args()

    endpoints = [args.endpoint] if args.endpoint else ENDPOINTS

    print("AgentVerse Performance Benchmark")
    print(f"  Base URL: {BASE_URL}")
    print(f"  Requests: {args.requests}")
    print(f"  Concurrency: {args.concurrency}")

    results = await run_benchmarks(endpoints, args.requests, args.concurrency)

    # Summary
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"{'='*60}")
    for r in results:
        latency = r.get("latency", {})
        print(f"  {r['url']}")
        print(f"    Avg: {latency.get('avg_ms', 'N/A')}ms | P95: {latency.get('p95_ms', 'N/A')}ms | RPS: {r.get('requests_per_second', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(main())