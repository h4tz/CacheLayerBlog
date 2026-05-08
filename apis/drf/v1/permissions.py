"""Lightweight RBAC permission classes for the DRF rail."""

from __future__ import annotations

from rest_framework import permissions

from apps.users.models import Role


class IsStaff(permissions.BasePermission):
    """Admin or staff role required."""

    message = "Staff role required"

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.role in (Role.ADMIN, Role.STAFF))
