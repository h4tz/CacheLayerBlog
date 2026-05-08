"""Ninja routes for /products/."""

from __future__ import annotations

from typing import Optional

from ninja import Query, Router

from schemas.common import Page, PageMeta
from schemas.products import ProductCreateIn, ProductOut, ProductStockUpdateIn
from services.product_service import ProductFilters, ProductService

from ..auth import JWTAuth, require_staff

router = Router(tags=["products"], auth=JWTAuth())


@router.get("/", response=Page[ProductOut])
def list_products(
    request,
    search: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    ordering: str = "-created_at",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    qs = ProductService().list_products(
        ProductFilters(
            search=search,
            category=category,
            min_price=min_price,
            max_price=max_price,
            ordering=ordering,
        )
    )
    total = qs.count()
    items = [ProductOut.from_model(p) for p in qs[(page - 1) * page_size : page * page_size]]
    return Page[ProductOut](items=items, meta=PageMeta(page=page, page_size=page_size, total=total))


@router.get("/{sku}", response=ProductOut)
def get_product(request, sku: str):
    return ProductOut.from_model(ProductService().get(sku))


@router.post("/", response={201: ProductOut})
def create_product(request, payload: ProductCreateIn):
    require_staff(request.user)
    product = ProductService().create(
        actor=request.user,
        sku=payload.sku,
        name=payload.name,
        category_name=payload.category,
        price=payload.price,
        stock=payload.stock,
        description=payload.description,
    )
    return 201, ProductOut.from_model(product)


@router.patch("/{sku}/stock", response=ProductOut)
def update_stock(request, sku: str, payload: ProductStockUpdateIn):
    require_staff(request.user)
    product = ProductService().update_stock(actor=request.user, sku=sku, stock=payload.stock)
    return ProductOut.from_model(product)
