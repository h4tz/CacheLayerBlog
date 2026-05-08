"""Lightweight observability helpers used across the codebase."""

from __future__ import annotations

import contextlib
import time
from typing import Iterator

from prometheus_client import Counter, Histogram

# Per-rail latency histogram for a precise DRF vs Ninja comparison.
RAIL_LATENCY = Histogram(
    "clb_rail_latency_seconds",
    "End-to-end request latency split by API rail",
    labelnames=("rail", "endpoint", "method", "status"),
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# Service / repository call counters for hotspot detection.
SERVICE_CALLS = Counter(
    "clb_service_calls_total",
    "Service-layer method invocations",
    labelnames=("service", "method", "outcome"),
)


@contextlib.contextmanager
def timed_rail(rail: str, endpoint: str, method: str) -> Iterator[dict[str, str]]:
    """Context manager to instrument a single API call.

    Used by the Ninja layer (DRF latency comes via django_prometheus middleware
    and our own RequestTimingMiddleware).
    """
    state: dict[str, str] = {"status": "200"}
    start = time.perf_counter()
    try:
        yield state
    finally:
        RAIL_LATENCY.labels(rail, endpoint, method, state["status"]).observe(
            time.perf_counter() - start
        )
