"""Persistence access for the user aggregate."""

from __future__ import annotations

from django.db.models import QuerySet

from apps.users.models import User
from core.exceptions import ConflictError

from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def by_email(self, email: str) -> User:
        return self.get(email=email)

    def email_taken(self, email: str) -> bool:
        return self.exists(email=email)

    def create_user(self, *, email: str, username: str, password: str, role: str) -> User:
        if self.email_taken(email):
            raise ConflictError("Email already registered", {"email": email})
        user = User(email=email, username=username, role=role)
        user.set_password(password)
        user.save()
        return user

    def list_active(self) -> QuerySet[User]:
        return self.queryset().filter(is_active=True).only("id", "email", "username", "role")
