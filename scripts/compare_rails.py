"""Quick A/B comparison: hit both rails N times in-process and report stats.

This is *not* a replacement for Locust. It is a 30-second sanity check you
can run after a code change to see if you broke latency parity.
"""

from __future__ import annotations

import os
import statistics
import time

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.local")
django.setup()

from django.test import Client  # noqa: E402

from services.auth_service import AuthService  # noqa: E402
from tests.factories import ProductFactory, UserFactory  # noqa: E402

ITER = int(os.environ.get("ITER", "200"))


def setup() -> tuple[Client, dict, str]:
    user = UserFactory()
    product = ProductFactory()
    tokens = AuthService._issue(user)  # noqa: SLF001
    headers = {"HTTP_AUTHORIZATION": f"Bearer {tokens.access}"}
    return Client(), headers, product.sku


def time_path(client: Client, headers: dict, path: str, iters: int) -> list[float]:
    samples: list[float] = []
    for _ in range(iters):
        start = time.perf_counter()
        client.get(path, **headers)
        samples.append((time.perf_counter() - start) * 1000.0)
    return samples


def report(name: str, samples: list[float]) -> None:
    samples.sort()

    def pct(p: float) -> float:
        return samples[int(len(samples) * p)]

    print(
        f"{name:30} mean={statistics.mean(samples):7.2f}ms "
        f"p50={pct(0.5):7.2f}ms p95={pct(0.95):7.2f}ms p99={pct(0.99):7.2f}ms"
    )


def main() -> None:
    client, headers, sku = setup()

    cases = [
        ("DRF health", "/api/v1/drf/health/"),
        ("Ninja health", "/api/v1/ninja/health"),
        ("DRF product detail", f"/api/v1/drf/products/{sku}/"),
        ("Ninja product detail", f"/api/v1/ninja/products/{sku}"),
    ]
    for label, path in cases:
        report(label, time_path(client, headers, path, ITER))


if __name__ == "__main__":
    main()
