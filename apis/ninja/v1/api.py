"""Top-level Ninja v1 API.

Mounts the per-domain routers and registers the shared exception handler
so DRF and Ninja emit identical error envelopes.
"""

from __future__ import annotations

from ninja import NinjaAPI
from ninja.errors import ValidationError as NinjaValidationError

from core.exceptions import DomainError, ValidationError, ninja_exception_handler
from schemas.common import HealthOut

from .routers.auth_router import router as auth_router
from .routers.order_router import router as order_router
from .routers.product_router import router as product_router

api = NinjaAPI(
    title="CacheLayer Ninja API",
    version="1.0.0",
    urls_namespace="ninja_v1",
    docs_url="/docs",
)


@api.get("/health", response=HealthOut, auth=None, tags=["meta"])
def health(request):
    return HealthOut(status="ok", rail="ninja", version="1.0.0")


api.add_router("/auth", auth_router)
api.add_router("/products", product_router)
api.add_router("/orders", order_router)


@api.exception_handler(DomainError)
def handle_domain_error(request, exc: DomainError):
    return ninja_exception_handler(request, exc)


@api.exception_handler(NinjaValidationError)
def handle_validation(request, exc: NinjaValidationError):
    return ninja_exception_handler(
        request,
        ValidationError("Validation failed", {"errors": exc.errors}),
    )
