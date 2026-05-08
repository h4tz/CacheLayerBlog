"""Test factories for users, products and orders."""

from __future__ import annotations

from decimal import Decimal

import factory
from factory.django import DjangoModelFactory

from apps.catalog.models import Category, Product
from apps.orders.models import Order, OrderItem
from apps.users.models import Role, User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    role = Role.CUSTOMER

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", "password123")
        user = model_class(*args, **kwargs)
        user.set_password(password)
        user.save()
        return user


class StaffFactory(UserFactory):
    role = Role.STAFF


class AdminFactory(UserFactory):
    role = Role.ADMIN


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.LazyAttribute(lambda o: o.name.lower().replace(" ", "-"))


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    sku = factory.Sequence(lambda n: f"SKU-{n:06d}")
    name = factory.Sequence(lambda n: f"Product {n}")
    description = "Lorem ipsum"
    price = Decimal("19.99")
    stock = 100
    is_active = True
    category = factory.SubFactory(CategoryFactory)


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    note = ""


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1
    unit_price = Decimal("19.99")
