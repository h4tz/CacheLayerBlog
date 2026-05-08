"""Locust user class for the DRF rail."""

from __future__ import annotations

from .common import _BaseRailUser


class DRFUser(_BaseRailUser):
    rail_prefix = "/api/v1/drf"
    health_path = "/api/v1/drf/health/"
