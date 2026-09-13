"""Unit tests for ProductService."""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.core.cache import cache

from apps.catalog.models import Product
from apps.users.models import Role
from core.exceptions import PermissionDeniedError
from services.product_service import ProductFilters, ProductService
from tests.factories import CategoryFactory, ProductFactory, UserFactory


@pytest.mark.django_db
class TestListProducts:
    def test_returns_active_products(self):
        active = ProductFactory(is_active=True)
        ProductFactory(is_active=False)
        svc = ProductService()
        qs = svc.list_products(ProductFilters())
        assert active in qs
        assert qs.count() == 1

    def test_search_filter(self):
        p = ProductFactory(name="Espresso Blend")
        ProductFactory(name="Green Tea")
        svc = ProductService()
        qs = svc.list_products(ProductFilters(search="espresso"))
        assert p in qs

    def test_category_filter(self):
        cat = CategoryFactory(slug="coffee")
        p = ProductFactory(category=cat)
        ProductFactory()
        svc = ProductService()
        qs = svc.list_products(ProductFilters(category="coffee"))
        assert p in qs

    def test_price_range_filter(self):
        cheap = ProductFactory(price=Decimal("5.00"))
        expensive = ProductFactory(price=Decimal("50.00"))
        svc = ProductService()
        qs = svc.list_products(ProductFilters(min_price=10, max_price=100))
        assert cheap not in qs
        assert expensive in qs


@pytest.mark.django_db
class TestGetProduct:
    def test_caches_on_first_call(self):
        p = ProductFactory(sku="SKU-TEST")
        svc = ProductService()
        result = svc.get("SKU-TEST")
        assert result.sku == "SKU-TEST"
        cache_key = f"products:detail:v1:SKU-TEST"
        assert cache.get(cache_key) is not None

    def test_returns_cached_on_second_call(self):
        p = ProductFactory(sku="SKU-CACHED")
        svc = ProductService()
        svc.get("SKU-CACHED")
        original_name = p.name
        # Mutate DB directly — cache should still return old value
        Product.objects.filter(sku="SKU-CACHED").update(name="Changed")
        result = svc.get("SKU-CACHED")
        assert result.name == original_name


@pytest.mark.django_db
class TestCreateProduct:
    def test_staff_can_create(self):
        actor = UserFactory(role=Role.STAFF)
        svc = ProductService()
        product = svc.create(
            actor=actor,
            sku="SKU-NEW",
            name="Latte",
            category_name="Coffee",
            price=Decimal("4.50"),
            stock=10,
        )
        assert product.sku == "SKU-NEW"

    def test_customer_cannot_create(self):
        actor = UserFactory(role=Role.CUSTOMER)
        svc = ProductService()
        with pytest.raises(PermissionDeniedError):
            svc.create(
                actor=actor,
                sku="SKU-NOPE",
                name="Fail",
                category_name="X",
                price=Decimal("1.00"),
                stock=1,
            )

    def test_creates_category_automatically(self):
        actor = UserFactory(role=Role.STAFF)
        svc = ProductService()
        product = svc.create(
            actor=actor,
            sku="SKU-CAT",
            name="Mocha",
            category_name="Specialty Drinks",
            price=Decimal("5.00"),
            stock=5,
        )
        assert product.category.slug == "specialty-drinks"


@pytest.mark.django_db
class TestUpdateStock:
    def test_staff_can_update(self):
        actor = UserFactory(role=Role.STAFF)
        p = ProductFactory(sku="SKU-STOCK", stock=10)
        svc = ProductService()
        updated = svc.update_stock(actor=actor, sku="SKU-STOCK", stock=50)
        assert updated.stock == 50

    def test_customer_cannot_update(self):
        actor = UserFactory(role=Role.CUSTOMER)
        ProductFactory(sku="SKU-NOUPD")
        svc = ProductService()
        with pytest.raises(PermissionDeniedError):
            svc.update_stock(actor=actor, sku="SKU-NOUPD", stock=0)
