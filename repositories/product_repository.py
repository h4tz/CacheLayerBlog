"""Persistence access for the catalog aggregate."""

from __future__ import annotations

from django.db.models import Q, QuerySet

from apps.catalog.models import Category, Product

from .base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    model = Category

    def get_or_create_by_slug(self, *, name: str, slug: str | None = None) -> Category:
        slug = slug or name.lower().replace(" ", "-")
        obj, _ = Category.objects.get_or_create(slug=slug, defaults={"name": name})
        return obj


class ProductRepository(BaseRepository[Product]):
    model = Product

    def queryset(self) -> QuerySet[Product]:
        return Product.objects.select_related("category")

    def list_active(
        self,
        *,
        search: str | None = None,
        category: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        ordering: str = "-created_at",
    ) -> QuerySet[Product]:
        qs = self.queryset().filter(is_active=True)
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(sku__icontains=search))
        if category:
            qs = qs.filter(category__slug=category)
        if min_price is not None:
            qs = qs.filter(price__gte=min_price)
        if max_price is not None:
            qs = qs.filter(price__lte=max_price)
        return qs.order_by(ordering)

    def get_by_sku(self, sku: str) -> Product:
        return self.get(sku=sku)
