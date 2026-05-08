"""URL map for the DRF v1 rail."""

from django.urls import path

from . import views

app_name = "drf_v1"

urlpatterns = [
    path("health/", views.health, name="health"),

    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/me/", views.MeView.as_view(), name="me"),

    path("products/", views.ProductListCreateView.as_view(), name="product-list"),
    path("products/<str:sku>/", views.ProductDetailView.as_view(), name="product-detail"),
    path("products/<str:sku>/stock/", views.ProductStockView.as_view(), name="product-stock"),

    path("orders/", views.OrderListCreateView.as_view(), name="order-list"),
    path("orders/<int:order_id>/", views.OrderDetailView.as_view(), name="order-detail"),
    path("orders/<int:order_id>/status/", views.OrderStatusView.as_view(), name="order-status"),
]
