"""Smoke tests: both rails must respond and report their identity."""

from __future__ import annotations

import pytest


@pytest.mark.django_db
def test_drf_health(api_client):
    resp = api_client.get("/api/v1/drf/health/")
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"status": "ok", "rail": "drf", "version": "1.0.0"}


@pytest.mark.django_db
def test_ninja_health(api_client):
    resp = api_client.get("/api/v1/ninja/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["rail"] == "ninja"
    assert body["status"] == "ok"


@pytest.mark.django_db
def test_request_id_header_present(api_client):
    resp = api_client.get("/api/v1/drf/health/")
    assert "X-Request-ID" in resp.headers
    assert "X-Response-Time-Ms" in resp.headers
