"""Unit tests for OrderService."""

from __future__ import annotations

from decimal import Decimal

import pytest

from apps.orders.models import OrderStatus
from apps.users.models import Role
from core.exceptions import ConflictError, PermissionDeniedError, ValidationError
from services.order_service import OrderLineRequest, OrderService
from tests.factories import OrderFactory, ProductFactory, UserFactory


@pytest.mark.django_db
class TestPlaceOrder:
    def test_creates_order_with_correct_total(self):
        actor = UserFactory()
        p = ProductFactory(price=Decimal("10.00"), stock=5)
        svc = OrderService()
        order = svc.place_order(
            actor=actor,
            lines=[OrderLineRequest(product_sku=p.sku, quantity=3)],
        )
        assert order.total == Decimal("30.00")
        p.refresh_from_db()
        assert p.stock == 2

    def test_rejects_empty_lines(self):
        actor = UserFactory()
        svc = OrderService()
        with pytest.raises(ValidationError):
            svc.place_order(actor=actor, lines=[])

    def test_rejects_zero_quantity(self):
        actor = UserFactory()
        p = ProductFactory(stock=10)
        svc = OrderService()
        with pytest.raises(ValidationError):
            svc.place_order(
                actor=actor,
                lines=[OrderLineRequest(product_sku=p.sku, quantity=0)],
            )

    def test_rejects_insufficient_stock(self):
        actor = UserFactory()
        p = ProductFactory(stock=2)
        svc = OrderService()
        with pytest.raises(ConflictError):
            svc.place_order(
                actor=actor,
                lines=[OrderLineRequest(product_sku=p.sku, quantity=5)],
            )

    def test_multi_line_order(self):
        actor = UserFactory()
        p1 = ProductFactory(price=Decimal("5.00"), stock=10)
        p2 = ProductFactory(price=Decimal("3.00"), stock=10)
        svc = OrderService()
        order = svc.place_order(
            actor=actor,
            lines=[
                OrderLineRequest(product_sku=p1.sku, quantity=2),
                OrderLineRequest(product_sku=p2.sku, quantity=1),
            ],
        )
        assert order.total == Decimal("13.00")


@pytest.mark.django_db
class TestListFor:
    def test_customer_sees_own_orders(self):
        owner = UserFactory()
        other = UserFactory()
        OrderFactory(user=owner)
        OrderFactory(user=other)
        svc = OrderService()
        qs = svc.list_for(actor=owner)
        assert qs.count() == 1

    def test_staff_sees_all_orders(self):
        staff = UserFactory(role=Role.STAFF)
        OrderFactory()
        OrderFactory()
        svc = OrderService()
        qs = svc.list_for(actor=staff)
        assert qs.count() == 2


@pytest.mark.django_db
class TestGetFor:
    def test_owner_can_get_own_order(self):
        owner = UserFactory()
        order = OrderFactory(user=owner)
        svc = OrderService()
        result = svc.get_for(actor=owner, order_id=order.id)
        assert result.id == order.id

    def test_customer_cannot_get_other_order(self):
        owner = UserFactory()
        other = UserFactory()
        order = OrderFactory(user=owner)
        svc = OrderService()
        with pytest.raises(PermissionDeniedError):
            svc.get_for(actor=other, order_id=order.id)

    def test_staff_can_get_any_order(self):
        staff = UserFactory(role=Role.STAFF)
        order = OrderFactory()
        svc = OrderService()
        result = svc.get_for(actor=staff, order_id=order.id)
        assert result.id == order.id


@pytest.mark.django_db
class TestTransition:
    def test_staff_can_transition(self):
        staff = UserFactory(role=Role.STAFF)
        order = OrderFactory()
        svc = OrderService()
        result = svc.transition(actor=staff, order_id=order.id, target=OrderStatus.PAID)
        assert result.status == OrderStatus.PAID

    def test_customer_cannot_transition(self):
        owner = UserFactory()
        order = OrderFactory(user=owner)
        svc = OrderService()
        with pytest.raises(PermissionDeniedError):
            svc.transition(actor=owner, order_id=order.id, target=OrderStatus.SHIPPED)
