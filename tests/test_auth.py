"""End-to-end auth tests for both rails."""

from __future__ import annotations

import json

import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    "endpoint",
    ["/api/v1/drf/auth/register/", "/api/v1/ninja/auth/register"],
)
def test_register_creates_customer(api_client, endpoint):
    payload = {"email": "alice@example.com", "username": "alice", "password": "secret123"}
    resp = api_client.post(endpoint, data=json.dumps(payload), content_type="application/json")
    assert resp.status_code == 201, resp.content
    body = resp.json()
    assert body["email"] == "alice@example.com"
    assert body["role"] == "customer"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "endpoint",
    ["/api/v1/drf/auth/login/", "/api/v1/ninja/auth/login"],
)
def test_login_returns_token_pair(api_client, user, endpoint):
    payload = {"email": user.email, "password": "password123"}
    resp = api_client.post(endpoint, data=json.dumps(payload), content_type="application/json")
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert "access" in body and "refresh" in body
