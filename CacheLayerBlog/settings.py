"""Backwards-compatible shim.

Historically this file contained all settings. The project now uses
``core.settings.{local,test,prod}``. This module simply re-exports the
selected environment so legacy imports keep working.
"""

import os

env_module = os.environ.get("DJANGO_SETTINGS_MODULE", "core.settings.local")
if env_module == "CacheLayerBlog.settings":
    env_module = "core.settings.local"

_loaded = __import__(env_module, fromlist=["*"])
globals().update({k: v for k, v in _loaded.__dict__.items() if not k.startswith("_")})
