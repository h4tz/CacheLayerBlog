"""Ninja routes for /orders/."""

from __future__ import annotations

from ninja import Query, Router

from apps.orders.models import OrderStatus
from schemas.common import Page, PageMeta
from schemas.orders import OrderCreateIn, OrderOut, OrderStatusIn
from services.order_service import OrderLineRequest, OrderService

from ..auth import JWTAuth

router = Router(tags=["orders"], auth=JWTAuth())


@router.get("/", response=Page[OrderOut])
def list_orders(
    request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    qs = OrderService().list_for(actor=request.user)
    total = qs.count()
    items = [OrderOut.from_model(o) for o in qs[(page - 1) * page_size : page * page_size]]
    return Page[OrderOut](items=items, meta=PageMeta(page=page, page_size=page_size, total=total))


@router.post("/", response={201: OrderOut})
def create_order(request, payload: OrderCreateIn):
    lines = [OrderLineRequest(product_sku=l.product_sku, quantity=l.quantity) for l in payload.lines]
    order = OrderService().place_order(actor=request.user, lines=lines, note=payload.note)
    return 201, OrderOut.from_model(order)


@router.get("/{order_id}", response=OrderOut)
def get_order(request, order_id: int):
    order = OrderService().get_for(actor=request.user, order_id=order_id)
    return OrderOut.from_model(order)


@router.patch("/{order_id}/status", response=OrderOut)
def update_status(request, order_id: int, payload: OrderStatusIn):
    order = OrderService().transition(
        actor=request.user, order_id=order_id, target=OrderStatus(payload.status)
    )
    return OrderOut.from_model(order)
