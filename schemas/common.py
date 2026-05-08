"""Shared schema fragments used across Ninja routers."""

from __future__ import annotations

from typing import Generic, TypeVar

from ninja import Schema

T = TypeVar("T")


class PageMeta(Schema):
    page: int
    page_size: int
    total: int


class Page(Schema, Generic[T]):
    items: list[T]
    meta: PageMeta


class HealthOut(Schema):
    status: str
    rail: str
    version: str = "1.0.0"
