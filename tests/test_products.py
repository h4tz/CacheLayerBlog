"""Product API tests across both rails."""

from __future__ import annotations

import json

import pytest

from .factories import CategoryFactory, ProductFactory


@pytest.mark.django_db
@pytest.mark.parametrize(
    "endpoint",
    ["/api/v1/drf/products/", "/api/v1/ninja/products/"],
)
def test_list_products_paginates(api_client, auth_headers, endpoint):
    cat = CategoryFactory()
    for _ in range(5):
        ProductFactory(category=cat)
    resp = api_client.get(endpoint + "?page=1&page_size=3", **auth_headers)
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["meta"]["total"] == 5
    assert len(body["items"]) == 3


@pytest.mark.django_db
def test_create_product_requires_staff(api_client, auth_headers):
    payload = {
        "sku": "SKU-001",
        "name": "Espresso",
        "category": "Coffee",
        "price": "9.50",
        "stock": 5,
    }
    resp = api_client.post(
        "/api/v1/drf/products/",
        data=json.dumps(payload),
        content_type="application/json",
        **auth_headers,
    )
    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_create_product_succeeds_for_staff(api_client, staff_headers):
    payload = {
        "sku": "SKU-100",
        "name": "Mocha",
        "category": "Coffee",
        "price": "11.00",
        "stock": 10,
    }
    resp = api_client.post(
        "/api/v1/ninja/products/",
        data=json.dumps(payload),
        content_type="application/json",
        **staff_headers,
    )
    assert resp.status_code == 201, resp.content
    assert resp.json()["sku"] == "SKU-100"
