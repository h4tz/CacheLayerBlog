"""Product catalog use-cases."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.core.cache import cache

from apps.catalog.models import Product
from apps.users.models import Role, User
from core.exceptions import PermissionDeniedError
from repositories.product_repository import CategoryRepository, ProductRepository

PRODUCT_LIST_CACHE_KEY = "products:list:v1"
PRODUCT_DETAIL_CACHE_KEY = "products:detail:v1:{sku}"
DEFAULT_CACHE_TTL = 30  # seconds


@dataclass(slots=True)
class ProductFilters:
    search: str | None = None
    category: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    ordering: str = "-created_at"


class ProductService:
    def __init__(
        self,
        products: ProductRepository | None = None,
        categories: CategoryRepository | None = None,
    ) -> None:
        self.products = products or ProductRepository()
        self.categories = categories or CategoryRepository()

    def list_products(self, filters: ProductFilters):
        return self.products.list_active(
            search=filters.search,
            category=filters.category,
            min_price=filters.min_price,
            max_price=filters.max_price,
            ordering=filters.ordering,
        )

    def get(self, sku: str) -> Product:
        cache_key = PRODUCT_DETAIL_CACHE_KEY.format(sku=sku)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        product = self.products.get_by_sku(sku)
        cache.set(cache_key, product, DEFAULT_CACHE_TTL)
        return product

    def create(
        self,
        *,
        actor: User,
        sku: str,
        name: str,
        category_name: str,
        price: Decimal,
        stock: int,
        description: str = "",
    ) -> Product:
        self._require_staff(actor)
        category = self.categories.get_or_create_by_slug(name=category_name)
        product = Product.objects.create(
            sku=sku,
            name=name,
            category=category,
            price=price,
            stock=stock,
            description=description,
        )
        self._invalidate_caches(sku=sku)
        return product

    def update_stock(self, *, actor: User, sku: str, stock: int) -> Product:
        self._require_staff(actor)
        product = self.products.get_by_sku(sku)
        product.stock = stock
        product.save(update_fields=["stock", "updated_at"])
        self._invalidate_caches(sku=sku)
        return product

    @staticmethod
    def _require_staff(actor: User) -> None:
        if actor.role not in (Role.ADMIN, Role.STAFF):
            raise PermissionDeniedError("Staff role required")

    @staticmethod
    def _invalidate_caches(*, sku: str) -> None:
        cache.delete(PRODUCT_DETAIL_CACHE_KEY.format(sku=sku))
        cache.delete(PRODUCT_LIST_CACHE_KEY)
