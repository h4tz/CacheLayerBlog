"""Micro-benchmarks for validation: DRF serializers vs Pydantic schemas.

These tests do NOT spin up an HTTP server. They isolate the cost of the
validation/serialization layer alone, which is most of the difference
people see between DRF and Ninja in real workloads.
"""

from __future__ import annotations

import pytest

from apis.drf.v1.serializers import OrderCreateSerializer, ProductCreateSerializer
from schemas.orders import OrderCreateIn
from schemas.products import ProductCreateIn

PRODUCT_PAYLOAD = {
    "sku": "SKU-1",
    "name": "Espresso",
    "category": "Coffee",
    "price": "9.50",
    "stock": 10,
    "description": "Strong",
}

ORDER_PAYLOAD = {
    "note": "n",
    "lines": [{"product_sku": f"BENCH-{i:08d}", "quantity": (i % 5) + 1} for i in range(20)],
}


@pytest.mark.benchmark(group="product-create-validation")
def test_drf_product_validation(benchmark):
    def run():
        s = ProductCreateSerializer(data=PRODUCT_PAYLOAD)
        s.is_valid(raise_exception=True)
        return s.validated_data

    benchmark(run)


@pytest.mark.benchmark(group="product-create-validation")
def test_pydantic_product_validation(benchmark):
    def run():
        return ProductCreateIn(**PRODUCT_PAYLOAD)

    benchmark(run)


@pytest.mark.benchmark(group="order-create-validation")
def test_drf_order_validation(benchmark):
    def run():
        s = OrderCreateSerializer(data=ORDER_PAYLOAD)
        s.is_valid(raise_exception=True)
        return s.validated_data

    benchmark(run)


@pytest.mark.benchmark(group="order-create-validation")
def test_pydantic_order_validation(benchmark):
    def run():
        return OrderCreateIn(**ORDER_PAYLOAD)

    benchmark(run)
