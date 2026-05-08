"""Pydantic schemas for the users domain (Ninja rail)."""

from __future__ import annotations

from ninja import Schema
from pydantic import EmailStr


class RegisterIn(Schema):
    email: EmailStr
    username: str
    password: str


class LoginIn(Schema):
    email: EmailStr
    password: str


class UserOut(Schema):
    id: int
    email: EmailStr
    username: str
    role: str


class TokenPairOut(Schema):
    access: str
    refresh: str
