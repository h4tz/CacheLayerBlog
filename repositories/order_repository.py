"""Persistence access for the order aggregate."""

from __future__ import annotations

from django.db.models import QuerySet

from apps.orders.models import Order, OrderItem

from .base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    model = Order

    def queryset(self) -> QuerySet[Order]:
        return (
            Order.objects.select_related("user")
            .prefetch_related("items__product")
        )

    def for_user(self, user_id: int) -> QuerySet[Order]:
        return self.queryset().filter(user_id=user_id)

    def create_with_items(
        self, *, user_id: int, note: str, items: list[OrderItem]
    ) -> Order:
        order = Order.objects.create(user_id=user_id, note=note)
        for item in items:
            item.order = order
            item.save()
        return order
