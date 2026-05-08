"""Settings package.

The active settings module is selected via the ``DJANGO_SETTINGS_MODULE``
environment variable (default: ``core.settings.local``). Each environment
inherits from ``base.py`` so shared concerns (apps, middleware, logging) live
in one place and only deltas are expressed per-env.
"""
