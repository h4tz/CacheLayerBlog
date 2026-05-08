"""HTTP middleware that is independent of any API framework.

These run for both the DRF rail and the Ninja rail, so request-id and timing
metrics are comparable across the two surfaces.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Callable

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger("clb.request")

REQUEST_ID_HEADER = "X-Request-ID"
RESPONSE_TIME_HEADER = "X-Response-Time-Ms"


class RequestIDMiddleware:
    """Attach a stable request id to every request and propagate it on the response.

    A correlation id is the cheapest observability win you can implement.
    Logs, traces, and downstream services can all join on it later.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        rid = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        request.request_id = rid  # type: ignore[attr-defined]
        response = self.get_response(request)
        response[REQUEST_ID_HEADER] = rid
        return response


class RequestTimingMiddleware:
    """Record per-request wall-clock time and emit a structured log line.

    The middleware deliberately avoids any per-framework hooks so DRF and
    Ninja routes are measured identically.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start = time.perf_counter()
        response = self.get_response(request)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        response[RESPONSE_TIME_HEADER] = f"{elapsed_ms:.2f}"
        logger.info(
            "request.completed",
            extra={
                "request_id": getattr(request, "request_id", None),
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "elapsed_ms": round(elapsed_ms, 3),
                "rail": _detect_rail(request.path),
            },
        )
        return response


def _detect_rail(path: str) -> str:
    """Tag a request with the framework rail it hit (drf|ninja|other)."""
    if path.startswith("/api/v1/drf/"):
        return "drf"
    if path.startswith("/api/v1/ninja/"):
        return "ninja"
    return "other"
