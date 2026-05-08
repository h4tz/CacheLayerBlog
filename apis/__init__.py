"""API rails: thin transport-only layers.

- ``apis.drf`` mounts under /api/v1/drf/
- ``apis.ninja`` mounts under /api/v1/ninja/

Both call the same services. Differences here are *only* serialization,
validation, and routing engine.
"""
