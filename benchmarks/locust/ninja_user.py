"""Locust user class for the Ninja rail."""

from __future__ import annotations

from .common import _BaseRailUser


class NinjaUser(_BaseRailUser):
    rail_prefix = "/api/v1/ninja"
    health_path = "/api/v1/ninja/health"
