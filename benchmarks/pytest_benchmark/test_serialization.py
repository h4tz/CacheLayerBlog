"""Output-side serialization benchmarks.

We compare DRF model serializer dumps vs Ninja Schema construction for
the product detail payload. Both rails read from the *same* model
instance.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from apis.drf.v1.serializers import ProductSerializer
from apps.catalog.models import Category, Product
from schemas.products import ProductOut


@pytest.fixture
def product(db):
    cat = Category.objects.create(name="Coffee", slug="coffee")
    return Product.objects.create(
        sku="SKU-OUT-1",
        name="Espresso",
        slug="sku-out-1-espresso",
        description="x" * 200,
        price=Decimal("9.50"),
        stock=10,
        category=cat,
    )


@pytest.mark.django_db
@pytest.mark.benchmark(group="product-serialization")
def test_drf_serialize_product(benchmark, product):
    def run():
        return ProductSerializer(product).data

    benchmark(run)


@pytest.mark.django_db
@pytest.mark.benchmark(group="product-serialization")
def test_ninja_serialize_product(benchmark, product):
    def run():
        out = ProductOut.from_model(product)
        return out.model_dump() if hasattr(out, "model_dump") else out.dict()

    benchmark(run)
