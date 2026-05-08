"""DRF v1 views.

Each view is *only* responsible for:
- HTTP plumbing (status codes, query params, headers),
- DRF serializer validation,
- delegating to a service.

Business rules and DB access are NOT allowed here.
"""

from __future__ import annotations

from decimal import Decimal

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import OrderStatus
from services.auth_service import AuthService
from services.order_service import OrderLineRequest, OrderService
from services.product_service import ProductFilters, ProductService

from .permissions import IsStaff
from .serializers import (
    HealthSerializer,
    LoginSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusSerializer,
    ProductCreateSerializer,
    ProductSerializer,
    ProductStockSerializer,
    RegisterSerializer,
    TokenPairSerializer,
    UserSerializer,
)


# ---- Health ----
@api_view(["GET"])
@permission_classes([AllowAny])
def health(request: Request) -> Response:
    payload = {"status": "ok", "rail": "drf", "version": "1.0.0"}
    return Response(HealthSerializer(payload).data)


# ---- Auth ----
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = AuthService().register(**ser.validated_data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        tokens = AuthService().login(**ser.validated_data)
        return Response(TokenPairSerializer(tokens.to_dict()).data)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(UserSerializer(request.user).data)


# ---- Products ----
class ProductListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        filters = ProductFilters(
            search=request.query_params.get("search"),
            category=request.query_params.get("category"),
            min_price=_decimal(request.query_params.get("min_price")),
            max_price=_decimal(request.query_params.get("max_price")),
            ordering=request.query_params.get("ordering", "-created_at"),
        )
        page = int(request.query_params.get("page", 1))
        page_size = min(int(request.query_params.get("page_size", 20)), 100)
        qs = ProductService().list_products(filters)
        total = qs.count()
        items = list(qs[(page - 1) * page_size : page * page_size])
        return Response(
            {
                "items": ProductSerializer(items, many=True).data,
                "meta": {"page": page, "page_size": page_size, "total": total},
            }
        )

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsStaff()]
        return [IsAuthenticated()]

    def post(self, request: Request) -> Response:
        ser = ProductCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        product = ProductService().create(actor=request.user, **ser.validated_data)
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)


class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, sku: str) -> Response:
        product = ProductService().get(sku)
        return Response(ProductSerializer(product).data)


class ProductStockView(APIView):
    permission_classes = [IsAuthenticated, IsStaff]

    def patch(self, request: Request, sku: str) -> Response:
        ser = ProductStockSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        product = ProductService().update_stock(
            actor=request.user, sku=sku, stock=ser.validated_data["stock"]
        )
        return Response(ProductSerializer(product).data)


# ---- Orders ----
class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        page = int(request.query_params.get("page", 1))
        page_size = min(int(request.query_params.get("page_size", 20)), 100)
        qs = OrderService().list_for(actor=request.user)
        total = qs.count()
        items = list(qs[(page - 1) * page_size : page * page_size])
        return Response(
            {
                "items": OrderSerializer(items, many=True).data,
                "meta": {"page": page, "page_size": page_size, "total": total},
            }
        )

    def post(self, request: Request) -> Response:
        ser = OrderCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        lines = [OrderLineRequest(**line) for line in ser.validated_data["lines"]]
        order = OrderService().place_order(
            actor=request.user, lines=lines, note=ser.validated_data.get("note", "")
        )
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, order_id: int) -> Response:
        order = OrderService().get_for(actor=request.user, order_id=order_id)
        return Response(OrderSerializer(order).data)


class OrderStatusView(APIView):
    permission_classes = [IsAuthenticated, IsStaff]

    def patch(self, request: Request, order_id: int) -> Response:
        ser = OrderStatusSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        order = OrderService().transition(
            actor=request.user,
            order_id=order_id,
            target=OrderStatus(ser.validated_data["status"]),
        )
        return Response(OrderSerializer(order).data)


def _decimal(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
