"""Unit tests for repositories."""

from __future__ import annotations

from decimal import Decimal

import pytest

from apps.users.models import Role
from core.exceptions import ConflictError, NotFoundError
from repositories.order_repository import OrderRepository
from repositories.product_repository import CategoryRepository, ProductRepository
from repositories.user_repository import UserRepository
from tests.factories import (
    CategoryFactory,
    OrderFactory,
    ProductFactory,
    UserFactory,
)


@pytest.mark.django_db
class TestUserRepository:
    def test_by_email(self):
        user = UserFactory(email="test@example.com")
        repo = UserRepository()
        result = repo.by_email("test@example.com")
        assert result.id == user.id

    def test_by_email_not_found(self):
        repo = UserRepository()
        with pytest.raises(NotFoundError):
            repo.by_email("nope@example.com")

    def test_email_taken(self):
        UserFactory(email="taken@example.com")
        repo = UserRepository()
        assert repo.email_taken("taken@example.com") is True
        assert repo.email_taken("free@example.com") is False

    def test_create_user(self):
        repo = UserRepository()
        user = repo.create_user(email="new@example.com", username="new", password="pass12345", role=Role.CUSTOMER)
        assert user.email == "new@example.com"
        assert user.check_password("pass12345")

    def test_create_user_duplicate_raises(self):
        UserFactory(email="dup@example.com")
        repo = UserRepository()
        with pytest.raises(ConflictError):
            repo.create_user(email="dup@example.com", username="x", password="pass12345", role=Role.CUSTOMER)

    def test_list_active(self):
        UserFactory(is_active=True)
        UserFactory(is_active=False)
        repo = UserRepository()
        assert repo.list_active().count() == 1


@pytest.mark.django_db
class TestCategoryRepository:
    def test_get_or_create_creates(self):
        repo = CategoryRepository()
        cat = repo.get_or_create_by_slug(name="Coffee")
        assert cat.slug == "coffee"

    def test_get_or_create_returns_existing(self):
        existing = CategoryFactory(slug="tea", name="Tea")
        repo = CategoryRepository()
        cat = repo.get_or_create_by_slug(name="Tea")
        assert cat.id == existing.id

    def test_custom_slug(self):
        repo = CategoryRepository()
        cat = repo.get_or_create_by_slug(name="Specialty", slug="specialty-drinks")
        assert cat.slug == "specialty-drinks"


@pytest.mark.django_db
class TestProductRepository:
    def test_get_by_sku(self):
        p = ProductFactory(sku="SKU-123")
        repo = ProductRepository()
        result = repo.get_by_sku("SKU-123")
        assert result.id == p.id

    def test_list_active_filters(self):
        active = ProductFactory(is_active=True)
        ProductFactory(is_active=False)
        repo = ProductRepository()
        qs = repo.list_active()
        assert active in qs
        assert qs.count() == 1

    def test_list_active_search(self):
        p = ProductFactory(name="Espresso Machine")
        ProductFactory(name="Green Tea")
        repo = ProductRepository()
        qs = repo.list_active(search="espresso")
        assert p in qs

    def test_list_active_price_filter(self):
        cheap = ProductFactory(price=Decimal("5.00"))
        expensive = ProductFactory(price=Decimal("100.00"))
        repo = ProductRepository()
        qs = repo.list_active(min_price=20)
        assert cheap not in qs
        assert expensive in qs


@pytest.mark.django_db
class TestOrderRepository:
    def test_for_user_filters(self):
        user = UserFactory()
        OrderFactory(user=user)
        OrderFactory()
        repo = OrderRepository()
        qs = repo.for_user(user.id)
        assert qs.count() == 1

    def test_queryset_prefetches(self):
        OrderFactory()
        repo = OrderRepository()
        qs = repo.queryset()
        assert qs.count() == 1
