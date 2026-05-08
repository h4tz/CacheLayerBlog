"""Order placement tests."""

from __future__ import annotations

import json
from decimal import Decimal

import pytest

from .factories import ProductFactory


@pytest.mark.django_db
def test_place_order_decrements_stock(api_client, auth_headers):
    p = ProductFactory(stock=10, price=Decimal("5.00"))
    payload = {
        "note": "first order",
        "lines": [{"product_sku": p.sku, "quantity": 3}],
    }
    resp = api_client.post(
        "/api/v1/drf/orders/",
        data=json.dumps(payload),
        content_type="application/json",
        **auth_headers,
    )
    assert resp.status_code == 201, resp.content
    body = resp.json()
    assert Decimal(str(body["total"])) == Decimal("15.00")
    p.refresh_from_db()
    assert p.stock == 7


@pytest.mark.django_db
def test_insufficient_stock_returns_conflict(api_client, auth_headers):
    p = ProductFactory(stock=2)
    payload = {"lines": [{"product_sku": p.sku, "quantity": 5}]}
    resp = api_client.post(
        "/api/v1/ninja/orders/",
        data=json.dumps(payload),
        content_type="application/json",
        **auth_headers,
    )
    assert resp.status_code == 409, resp.content
    body = resp.json()
    assert body["error"]["code"] == "conflict"


@pytest.mark.django_db
def test_customers_only_see_their_own_orders(api_client, auth_headers, user):
    p = ProductFactory(stock=10)
    api_client.post(
        "/api/v1/drf/orders/",
        data=json.dumps({"lines": [{"product_sku": p.sku, "quantity": 1}]}),
        content_type="application/json",
        **auth_headers,
    )
    resp = api_client.get("/api/v1/drf/orders/", **auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["meta"]["total"] == 1
