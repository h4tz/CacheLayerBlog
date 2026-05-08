"""Background tasks for the orders aggregate."""

from __future__ import annotations

import logging

from celery import shared_task

from apps.orders.models import Order, OrderStatus

logger = logging.getLogger("clb.orders.tasks")


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def settle_order(self, order_id: int) -> str:
    """Stub: pretend to charge a payment and mark the order paid.

    In a real system this would call into a payment gateway service. The
    point here is to demonstrate the worker pattern without coupling it
    to any external SDK.
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:  # pragma: no cover - defensive
        logger.warning("settle_order: order %s missing", order_id)
        return "missing"

    order.status = OrderStatus.PAID
    order.save(update_fields=["status", "updated_at"])
    return "paid"
