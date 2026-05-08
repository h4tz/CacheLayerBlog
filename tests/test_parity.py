"""Cross-rail parity tests.

These tests *enforce* that DRF and Ninja agree on the response shape for the
same input. Any deviation is a benchmark-invalidating bug.
"""

from __future__ import annotations

import pytest

from .factories import ProductFactory


@pytest.mark.django_db
def test_product_payload_shape_matches(api_client, auth_headers):
    p = ProductFactory()

    drf = api_client.get(f"/api/v1/drf/products/{p.sku}/", **auth_headers).json()
    ninja = api_client.get(f"/api/v1/ninja/products/{p.sku}", **auth_headers).json()

    assert set(drf.keys()) == set(ninja.keys()), (drf.keys(), ninja.keys())
    for key in ("sku", "name", "slug", "category", "is_active"):
        assert drf[key] == ninja[key], key
