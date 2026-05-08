"""Shared pytest fixtures."""

from __future__ import annotations

import pytest
from django.test import Client

from .factories import AdminFactory, StaffFactory, UserFactory


@pytest.fixture
def api_client() -> Client:
    return Client()


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def staff(db):
    return StaffFactory()


@pytest.fixture
def admin(db):
    return AdminFactory()


@pytest.fixture
def auth_headers(user):
    """Issue a real JWT pair for the given user."""
    from services.auth_service import AuthService

    tokens = AuthService._issue(user)  # noqa: SLF001 - intentional
    return {"HTTP_AUTHORIZATION": f"Bearer {tokens.access}"}


@pytest.fixture
def staff_headers(staff):
    from services.auth_service import AuthService

    tokens = AuthService._issue(staff)  # noqa: SLF001
    return {"HTTP_AUTHORIZATION": f"Bearer {tokens.access}"}
