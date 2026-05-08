"""Local development settings."""

from .base import *  # noqa: F401,F403
from .base import INSTALLED_APPS, MIDDLEWARE

DEBUG = True
ALLOWED_HOSTS = ["*"]

INTERNAL_IPS = ["127.0.0.1"]

# Convenience: log SQL when DEBUG is on so we can see N+1 patterns locally.
LOGGING_CONFIG = None  # Configured manually in core.logging.configure_logging.
