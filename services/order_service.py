"""Order lifecycle use-cases."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction

from apps.orders.models import Order, OrderItem, OrderStatus
from apps.users.models import Role, User
from core.exceptions import ConflictError, PermissionDeniedError, ValidationError
from repositories.order_repository import OrderRepository
from repositories.product_repository import ProductRepository


@dataclass(slots=True, frozen=True)
class OrderLineRequest:
    product_sku: str
    quantity: int


class OrderService:
    def __init__(
        self,
        orders: OrderRepository | None = None,
        products: ProductRepository | None = None,
    ) -> None:
        self.orders = orders or OrderRepository()
        self.products = products or ProductRepository()

    @transaction.atomic
    def place_order(
        self,
        *,
        actor: User,
        lines: list[OrderLineRequest],
        note: str = "",
    ) -> Order:
        if not lines:
            raise ValidationError("Order requires at least one line")

        order = Order.objects.create(user=actor, note=note)
        total = Decimal("0")

        for line in lines:
            if line.quantity <= 0:
                raise ValidationError(
                    "Line quantity must be > 0",
                    {"sku": line.product_sku},
                )
            product = self.products.get_by_sku(line.product_sku)
            if not product.has_stock(line.quantity):
                raise ConflictError(
                    "Insufficient stock",
                    {"sku": product.sku, "requested": line.quantity, "available": product.stock},
                )
            product.reduce_stock(line.quantity)
            product.save(update_fields=["stock", "updated_at"])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=line.quantity,
                unit_price=product.price,
            )
            total += product.price * line.quantity

        order.total = total
        order.save(update_fields=["total", "updated_at"])
        return order

    def list_for(self, *, actor: User):
        if actor.role in (Role.ADMIN, Role.STAFF):
            return self.orders.queryset()
        return self.orders.for_user(actor.id)

    def get_for(self, *, actor: User, order_id: int) -> Order:
        order = self.orders.get(id=order_id)
        if actor.role not in (Role.ADMIN, Role.STAFF) and order.user_id != actor.id:
            raise PermissionDeniedError("You cannot view this order")
        return order

    def transition(self, *, actor: User, order_id: int, target: OrderStatus) -> Order:
        if actor.role not in (Role.ADMIN, Role.STAFF):
            raise PermissionDeniedError("Staff role required")
        order = self.orders.get(id=order_id)
        order.status = target
        order.save(update_fields=["status", "updated_at"])
        return order
