"""Shared helpers for Locust user classes.

The DRF and Ninja user classes inherit the same workload mix. The only
delta is the URL prefix. This is the entire point of the benchmark.
"""

from __future__ import annotations

import random

from locust import HttpUser, between, task


class _BaseRailUser(HttpUser):
    """Common behaviour: login once, then exercise list/detail/order endpoints."""

    abstract = True
    wait_time = between(0.05, 0.25)
    rail_prefix: str = ""  # /api/v1/drf or /api/v1/ninja
    health_path: str = ""  # health endpoint differs in trailing slash

    # Pool of pre-seeded benchmark accounts.
    USER_POOL_SIZE = 200

    def on_start(self) -> None:
        idx = random.randint(0, self.USER_POOL_SIZE - 1)
        self.email = f"bench{idx:06d}@bench.example"
        with self.client.post(
            f"{self.rail_prefix}/auth/login{self._slash()}",
            json={"email": self.email, "password": "benchpass"},
            catch_response=True,
            name=f"{self.rail_prefix}/auth/login",
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"login failed: {resp.status_code}")
                self.token = None
                return
            self.token = resp.json()["access"]
        self.client.headers.update({"Authorization": f"Bearer {self.token}"})

    def _slash(self) -> str:
        return "/" if self.rail_prefix.endswith("drf") else ""

    @task(10)
    def list_products(self) -> None:
        self.client.get(
            f"{self.rail_prefix}/products{self._slash()}?page=1&page_size=20",
            name=f"{self.rail_prefix}/products list",
        )

    @task(5)
    def get_product(self) -> None:
        sku = f"BENCH-{random.randint(0, 4999):08d}"
        self.client.get(
            f"{self.rail_prefix}/products/{sku}{self._slash() if self.rail_prefix.endswith('drf') else ''}",
            name=f"{self.rail_prefix}/products/<sku>",
        )

    @task(2)
    def place_order(self) -> None:
        sku = f"BENCH-{random.randint(0, 4999):08d}"
        self.client.post(
            f"{self.rail_prefix}/orders{self._slash()}",
            json={"lines": [{"product_sku": sku, "quantity": 1}]},
            name=f"{self.rail_prefix}/orders create",
        )

    @task(1)
    def health(self) -> None:
        self.client.get(self.health_path, name=f"{self.rail_prefix}/health")
