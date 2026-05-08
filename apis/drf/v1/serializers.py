"""DRF serializers for the v1 rail.

Pure transport-layer code: validation + (de)serialization. Anything else
(persistence, business rules) belongs in services or repositories.
"""

from __future__ import annotations

from rest_framework import serializers

from apps.catalog.models import Product
from apps.orders.models import Order, OrderItem
from apps.users.models import User


class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()
    rail = serializers.CharField()
    version = serializers.CharField()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField(min_length=8, write_only=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "username", "role")


class TokenPairSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="slug", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "sku",
            "name",
            "slug",
            "description",
            "price",
            "stock",
            "is_active",
            "category",
        )


class ProductCreateSerializer(serializers.Serializer):
    sku = serializers.CharField()
    name = serializers.CharField()
    category = serializers.CharField()
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    stock = serializers.IntegerField(default=0)
    description = serializers.CharField(allow_blank=True, default="")


class ProductStockSerializer(serializers.Serializer):
    stock = serializers.IntegerField(min_value=0)


class OrderLineSerializer(serializers.Serializer):
    product_sku = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True, default="")
    lines = OrderLineSerializer(many=True)


class OrderItemReadSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ("product_sku", "quantity", "unit_price", "line_total")

    def get_line_total(self, obj: OrderItem):
        return obj.unit_price * obj.quantity


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "status", "total", "note", "items")


class OrderStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
