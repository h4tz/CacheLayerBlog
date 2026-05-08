"""JWT auth for Ninja using SimpleJWT primitives.

We re-use SimpleJWT instead of rolling a parallel implementation: this
keeps DRF and Ninja on the same token format and prevents an
auth-mismatch bug class.
"""

from __future__ import annotations

from django.http import HttpRequest
from ninja.security import HttpBearer
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.users.models import User
from core.exceptions import PermissionDeniedError


class JWTAuth(HttpBearer):
    """Bearer token auth that returns the authenticated user."""

    def authenticate(self, request: HttpRequest, token: str) -> User | None:
        validator = JWTAuthentication()
        try:
            validated = validator.get_validated_token(token)
            user = validator.get_user(validated)
        except Exception:  # pragma: no cover - SimpleJWT raises various
            return None
        request.user = user
        return user


def require_staff(user: User) -> None:
    if not user or not user.is_staff_role:
        raise PermissionDeniedError("Staff role required")
