"""Authentication / registration use-cases."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import Role, User
from core.exceptions import PermissionDeniedError, ValidationError
from repositories.user_repository import UserRepository


@dataclass(slots=True, frozen=True)
class TokenPair:
    access: str
    refresh: str

    def to_dict(self) -> dict[str, str]:
        return {"access": self.access, "refresh": self.refresh}


class AuthService:
    def __init__(self, users: UserRepository | None = None) -> None:
        self.users = users or UserRepository()

    def register(self, *, email: str, username: str, password: str) -> User:
        if len(password) < 8:
            raise ValidationError("Password too short", {"min_length": 8})
        return self.users.create_user(
            email=email, username=username, password=password, role=Role.CUSTOMER
        )

    def login(self, *, email: str, password: str) -> TokenPair:
        user = authenticate(username=email, password=password)
        if user is None:
            raise PermissionDeniedError("Invalid credentials")
        return self._issue(user)

    @staticmethod
    def _issue(user: User) -> TokenPair:
        refresh = RefreshToken.for_user(user)
        refresh["role"] = user.role
        return TokenPair(access=str(refresh.access_token), refresh=str(refresh))

    @staticmethod
    def claims_from_user(user: User) -> dict[str, Any]:
        return {"sub": user.id, "email": user.email, "role": user.role}
