"""Default Locust file: runs both rails simultaneously.

Use ``--tags drf`` or ``--tags ninja`` to isolate one rail.
"""

from __future__ import annotations

from locust import tag

from .drf_user import DRFUser
from .ninja_user import NinjaUser


@tag("drf")
class DRF(DRFUser):
    weight = 1


@tag("ninja")
class Ninja(NinjaUser):
    weight = 1
