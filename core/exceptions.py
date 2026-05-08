"""Centralised exception types and error-envelope handlers.

Both rails (DRF and Ninja) use the same envelope so client code does not
need to branch. The envelope is intentionally minimal:

    {
        "error": {
            "code": "string",
            "message": "string",
            "details": {...}
        },
        "request_id": "string"
    }
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.http import HttpRequest, JsonResponse
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_handler


class DomainError(Exception):
    """Base class for predictable, user-facing business errors."""

    code: str = "domain_error"
    http_status: int = 400

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(DomainError):
    code = "not_found"
    http_status = 404


class PermissionDeniedError(DomainError):
    code = "permission_denied"
    http_status = 403


class ValidationError(DomainError):
    code = "validation_error"
    http_status = 422


class ConflictError(DomainError):
    code = "conflict"
    http_status = 409


@dataclass(slots=True)
class ErrorEnvelope:
    code: str
    message: str
    details: dict[str, Any]
    request_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            },
            "request_id": self.request_id,
        }


def envelope_for(request: HttpRequest, exc: DomainError) -> ErrorEnvelope:
    return ErrorEnvelope(
        code=exc.code,
        message=exc.message,
        details=exc.details,
        request_id=getattr(request, "request_id", None),
    )


# ---- DRF ----
def drf_exception_handler(exc, context):  # type: ignore[no-untyped-def]
    """Adapter that maps DRF exceptions and our DomainError into the envelope."""
    request = context.get("request")
    if isinstance(exc, DomainError):
        env = envelope_for(request, exc)
        return Response(env.to_dict(), status=exc.http_status)
    response = drf_default_handler(exc, context)
    if response is not None:
        env = ErrorEnvelope(
            code="drf_error",
            message=str(exc),
            details=response.data if isinstance(response.data, dict) else {"raw": response.data},
            request_id=getattr(request, "request_id", None),
        )
        return Response(env.to_dict(), status=response.status_code)
    return None


# ---- Ninja ----
def ninja_exception_handler(request: HttpRequest, exc: DomainError) -> JsonResponse:
    env = envelope_for(request, exc)
    return JsonResponse(env.to_dict(), status=exc.http_status)
