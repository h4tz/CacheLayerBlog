"""Celery application.

Discovered by Django via ``CacheLayerBlog/__init__.py`` lazy import inside
the worker entrypoint. Tasks live next to the domain that owns them
(e.g. ``apps.orders.tasks``).
"""

from __future__ import annotations

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.prod")

app = Celery("cachelayer")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
