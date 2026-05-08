"""Pydantic schemas for the orders domain (Ninja rail)."""

from __future__ import annotations

from decimal import Decimal

from ninja import Schema


class OrderLineIn(Schema):
    product_sku: str
    quantity: int


class OrderCreateIn(Schema):
    note: str = ""
    lines: list[OrderLineIn]


class OrderItemOut(Schema):
    product_sku: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class OrderOut(Schema):
    id: int
    status: str
    total: Decimal
    note: str
    items: list[OrderItemOut]

    @staticmethod
    def from_model(order) -> "OrderOut":
        return OrderOut(
            id=order.id,
            status=order.status,
            total=order.total,
            note=order.note,
            items=[
                OrderItemOut(
                    product_sku=item.product.sku,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    line_total=item.unit_price * item.quantity,
                )
                for item in order.items.all()
            ],
        )


class OrderStatusIn(Schema):
    status: str
