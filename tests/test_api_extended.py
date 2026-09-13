"""Additional API tests for auth/me, order detail, status transition, and RBAC denial."""

from __future__ import annotations

import json
from decimal import Decimal

import pytest

from .factories import OrderFactory, ProductFactory, UserFactory


# ── auth/me ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
@pytest.mark.parametrize(
    "endpoint",
    ["/api/v1/drf/auth/me/", "/api/v1/ninja/auth/me"],
)
def test_me_returns_current_user(api_client, user, auth_headers, endpoint):
    resp = api_client.get(endpoint, **auth_headers)
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["email"] == user.email
    assert body["role"] == "customer"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "endpoint",
    ["/api/v1/drf/auth/me/", "/api/v1/ninja/auth/me"],
)
def test_me_requires_auth(api_client, endpoint):
    resp = api_client.get(endpoint)
    assert resp.status_code in (401, 403)


# ── order detail ─────────────────────────────────────────────────────────


@pytest.mark.django_db
def test_order_detail_drf(api_client, auth_headers):
    p = ProductFactory(stock=10, price=Decimal("5.00"))
    create_resp = api_client.post(
        "/api/v1/drf/orders/",
        data=json.dumps({"lines": [{"product_sku": p.sku, "quantity": 1}]}),
        content_type="application/json",
        **auth_headers,
    )
    assert create_resp.status_code == 201
    order_id = create_resp.json()["id"]

    resp = api_client.get(f"/api/v1/drf/orders/{order_id}/", **auth_headers)
    assert resp.status_code == 200, resp.content
    assert resp.json()["id"] == order_id


@pytest.mark.django_db
def test_order_detail_ninja(api_client, auth_headers):
    p = ProductFactory(stock=10, price=Decimal("5.00"))
    create_resp = api_client.post(
        "/api/v1/ninja/orders/",
        data=json.dumps({"lines": [{"product_sku": p.sku, "quantity": 1}]}),
        content_type="application/json",
        **auth_headers,
    )
    assert create_resp.status_code == 201
    order_id = create_resp.json()["id"]

    resp = api_client.get(f"/api/v1/ninja/orders/{order_id}", **auth_headers)
    assert resp.status_code == 200, resp.content
    assert resp.json()["id"] == order_id


@pytest.mark.django_db
def test_customer_cannot_view_other_order_drf(api_client):
    owner = UserFactory()
    other = UserFactory()
    order = OrderFactory(user=owner)

    from services.auth_service import AuthService
    tokens = AuthService._issue(other)
    headers = {"HTTP_AUTHORIZATION": f"Bearer {tokens.access}"}

    resp = api_client.get(f"/api/v1/drf/orders/{order.id}/", **headers)
    assert resp.status_code == 403


@pytest.mark.django_db
def test_customer_cannot_view_other_order_ninja(api_client):
    owner = UserFactory()
    other = UserFactory()
    order = OrderFactory(user=owner)

    from services.auth_service import AuthService
    tokens = AuthService._issue(other)
    headers = {"HTTP_AUTHORIZATION": f"Bearer {tokens.access}"}

    resp = api_client.get(f"/api/v1/ninja/orders/{order.id}", **headers)
    assert resp.status_code == 403


# ── order status transition ──────────────────────────────────────────────


@pytest.mark.django_db
def test_staff_can_transition_order_status_drf(api_client, staff_headers):
    p = ProductFactory(stock=10, price=Decimal("5.00"))
    create_resp = api_client.post(
        "/api/v1/drf/orders/",
        data=json.dumps({"lines": [{"product_sku": p.sku, "quantity": 1}]}),
        content_type="application/json",
        **staff_headers,
    )
    order_id = create_resp.json()["id"]

    resp = api_client.patch(
        f"/api/v1/drf/orders/{order_id}/status/",
        data=json.dumps({"status": "paid"}),
        content_type="application/json",
        **staff_headers,
    )
    assert resp.status_code == 200, resp.content
    assert resp.json()["status"] == "paid"


@pytest.mark.django_db
def test_staff_can_transition_order_status_ninja(api_client, staff_headers):
    p = ProductFactory(stock=10, price=Decimal("5.00"))
    create_resp = api_client.post(
        "/api/v1/ninja/orders/",
        data=json.dumps({"lines": [{"product_sku": p.sku, "quantity": 1}]}),
        content_type="application/json",
        **staff_headers,
    )
    order_id = create_resp.json()["id"]

    resp = api_client.patch(
        f"/api/v1/ninja/orders/{order_id}/status",
        data=json.dumps({"status": "paid"}),
        content_type="application/json",
        **staff_headers,
    )
    assert resp.status_code == 200, resp.content
    assert resp.json()["status"] == "paid"


@pytest.mark.django_db
def test_customer_cannot_transition_order_status_drf(api_client, auth_headers):
    p = ProductFactory(stock=10, price=Decimal("5.00"))
    create_resp = api_client.post(
        "/api/v1/drf/orders/",
        data=json.dumps({"lines": [{"product_sku": p.sku, "quantity": 1}]}),
        content_type="application/json",
        **auth_headers,
    )
    order_id = create_resp.json()["id"]

    resp = api_client.patch(
        f"/api/v1/drf/orders/{order_id}/status/",
        data=json.dumps({"status": "shipped"}),
        content_type="application/json",
        **auth_headers,
    )
    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_customer_cannot_transition_order_status_ninja(api_client, auth_headers):
    p = ProductFactory(stock=10, price=Decimal("5.00"))
    create_resp = api_client.post(
        "/api/v1/ninja/orders/",
        data=json.dumps({"lines": [{"product_sku": p.sku, "quantity": 1}]}),
        content_type="application/json",
        **auth_headers,
    )
    order_id = create_resp.json()["id"]

    resp = api_client.patch(
        f"/api/v1/ninja/orders/{order_id}/status",
        data=json.dumps({"status": "shipped"}),
        content_type="application/json",
        **auth_headers,
    )
    assert resp.status_code in (401, 403)


# ── RBAC denial: product stock update ────────────────────────────────────


@pytest.mark.django_db
def test_customer_cannot_update_stock(api_client, auth_headers):
    p = ProductFactory(sku="SKU-RBAC-TEST")
    resp = api_client.patch(
        f"/api/v1/drf/products/{p.sku}/stock/",
        data=json.dumps({"stock": 999}),
        content_type="application/json",
        **auth_headers,
    )
    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_customer_cannot_update_stock_ninja(api_client, auth_headers):
    p = ProductFactory(sku="SKU-RBAC-NINJA")
    resp = api_client.patch(
        f"/api/v1/ninja/products/{p.sku}/stock",
        data=json.dumps({"stock": 999}),
        content_type="application/json",
        **auth_headers,
    )
    assert resp.status_code in (401, 403)


# ── RBAC denial: product create ──────────────────────────────────────────


@pytest.mark.django_db
def test_customer_cannot_create_product_ninja(api_client, auth_headers):
    payload = {
        "sku": "SKU-NO-CREATE",
        "name": "Nope",
        "category": "Fail",
        "price": "1.00",
        "stock": 1,
    }
    resp = api_client.post(
        "/api/v1/ninja/products/",
        data=json.dumps(payload),
        content_type="application/json",
        **auth_headers,
    )
    assert resp.status_code in (401, 403)
