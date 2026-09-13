"""Tests for the blog app."""

from __future__ import annotations

import pytest
from blog.models import Post


@pytest.fixture
def post(db):
    return Post.objects.create(
        title="Test Post",
        content="Test content here",
        slug="test-post",
    )


@pytest.fixture
def blog_auth_headers(user):
    from services.auth_service import AuthService
    tokens = AuthService._issue(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {tokens.access}"}


@pytest.mark.django_db
class TestBlogAPI:
    def test_post_list(self, api_client, post, blog_auth_headers):
        resp = api_client.get("/api/posts/", **blog_auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()["results"]) == 1

    def test_post_detail(self, api_client, post, blog_auth_headers):
        resp = api_client.get("/api/posts/test-post/", **blog_auth_headers)
        assert resp.status_code == 200
        assert resp.json()["title"] == "Test Post"

    def test_post_detail_not_found(self, api_client, blog_auth_headers):
        resp = api_client.get("/api/posts/no-such-post/", **blog_auth_headers)
        assert resp.status_code == 404


@pytest.mark.django_db
class TestBlogViews:
    def test_post_list_view(self, api_client, post):
        resp = api_client.get("/blog/")
        assert resp.status_code == 200

    def test_post_detail_view(self, api_client, post):
        resp = api_client.get("/blog/test-post/")
        assert resp.status_code == 200

    def test_post_detail_view_missing_slug_returns_200(self, api_client):
        resp = api_client.get("/blog/missing-slug/")
        assert resp.status_code == 200
