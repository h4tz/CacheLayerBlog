"""Unit tests for AuthService."""

from __future__ import annotations

import pytest

from apps.users.models import Role
from core.exceptions import ConflictError, PermissionDeniedError, ValidationError
from repositories.user_repository import UserRepository
from services.auth_service import AuthService, TokenPair


@pytest.mark.django_db
class TestRegister:
    def test_creates_customer_user(self):
        svc = AuthService()
        user = svc.register(email="bob@example.com", username="bob", password="securepass123")
        assert user.email == "bob@example.com"
        assert user.role == Role.CUSTOMER

    def test_rejects_short_password(self):
        svc = AuthService()
        with pytest.raises(ValidationError):
            svc.register(email="bob@example.com", username="bob", password="short")

    def test_rejects_duplicate_email(self):
        svc = AuthService()
        svc.register(email="bob@example.com", username="bob", password="securepass123")
        with pytest.raises(ConflictError):
            svc.register(email="bob@example.com", username="bob2", password="securepass123")


@pytest.mark.django_db
class TestLogin:
    def test_returns_token_pair(self, user):
        svc = AuthService()
        tokens = svc.login(email=user.email, password="password123")
        assert isinstance(tokens, TokenPair)
        assert tokens.access
        assert tokens.refresh

    def test_rejects_wrong_password(self, user):
        svc = AuthService()
        with pytest.raises(PermissionDeniedError):
            svc.login(email=user.email, password="wrongpassword")


@pytest.mark.django_db
class TestIssue:
    def test_token_contains_role_claim(self, staff):
        tokens = AuthService._issue(staff)
        assert tokens.access
        assert tokens.refresh

    def test_to_dict(self, user):
        tokens = AuthService._issue(user)
        d = tokens.to_dict()
        assert "access" in d
        assert "refresh" in d


@pytest.mark.django_db
class TestClaimsFromUser:
    def test_returns_expected_claims(self, user):
        claims = AuthService.claims_from_user(user)
        assert claims["sub"] == user.id
        assert claims["email"] == user.email
        assert claims["role"] == user.role
