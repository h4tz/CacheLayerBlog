"""cProfile a single endpoint to find hotspots.

Usage::

    DJANGO_SETTINGS_MODULE=core.settings.local \
        python scripts/profile_endpoint.py /api/v1/drf/products/?page=1 50

The third argument is the number of iterations.
"""

from __future__ import annotations

import cProfile
import os
import pstats
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.local")
django.setup()

from django.test import Client  # noqa: E402

from services.auth_service import AuthService  # noqa: E402
from tests.factories import UserFactory  # noqa: E402


def main(path: str, iterations: int) -> None:
    client = Client()
    user = UserFactory()
    tokens = AuthService._issue(user)  # noqa: SLF001

    headers = {"HTTP_AUTHORIZATION": f"Bearer {tokens.access}"}

    profiler = cProfile.Profile()
    profiler.enable()
    for _ in range(iterations):
        client.get(path, **headers)
    profiler.disable()

    stats = pstats.Stats(profiler).sort_stats("cumulative")
    stats.print_stats(40)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "/api/v1/drf/health/"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    main(target, n)
