"""Pydantic schemas for the catalog domain (Ninja rail)."""

from __future__ import annotations

from decimal import Decimal

from ninja import Schema


class ProductOut(Schema):
    id: int
    sku: str
    name: str
    slug: str
    description: str
    price: Decimal
    stock: int
    is_active: bool
    category: str

    @staticmethod
    def from_model(product) -> "ProductOut":
        return ProductOut(
            id=product.id,
            sku=product.sku,
            name=product.name,
            slug=product.slug,
            description=product.description,
            price=product.price,
            stock=product.stock,
            is_active=product.is_active,
            category=product.category.slug,
        )


class ProductCreateIn(Schema):
    sku: str
    name: str
    category: str
    price: Decimal
    stock: int = 0
    description: str = ""


class ProductStockUpdateIn(Schema):
    stock: int
