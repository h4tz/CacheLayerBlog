"""User domain model with built-in role support.

Why a custom user from day one:
- Adding new fields to ``auth.User`` later is invasive.
- Roles drive RBAC checks across services and stay close to the model.
"""

from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = "admin", "Admin"
    STAFF = "staff", "Staff"
    CUSTOMER = "customer", "Customer"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.CUSTOMER)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users_user"
        indexes = [models.Index(fields=["role"])]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.email} ({self.role})"

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN

    @property
    def is_staff_role(self) -> bool:
        return self.role in (Role.ADMIN, Role.STAFF)
