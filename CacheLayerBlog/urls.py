"""Top-level URL configuration.

The app exposes three rails:

- ``/api/v1/drf/``     - Django REST Framework routes
- ``/api/v1/ninja/``   - Django Ninja routes
- ``/blog/``           - Legacy blog views (kept as a comparison baseline)

All public APIs are versioned under ``/api/v{n}/``.
"""

from django.contrib import admin
from django.urls import include, path

from apis.ninja.v1.api import api as ninja_api_v1

urlpatterns = [
    path("admin/", admin.site.urls),

    # DRF rail
    path("api/v1/drf/", include("apis.drf.v1.urls")),

    # Ninja rail
    path("api/v1/ninja/", ninja_api_v1.urls),

    # Legacy blog (kept for comparison and historical reference)
    path("blog/", include("blog.urls")),
    path("api/", include("blog.api_urls")),

    # Prometheus scrape endpoint
    path("", include("django_prometheus.urls")),
]
