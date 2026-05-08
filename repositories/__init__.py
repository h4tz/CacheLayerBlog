"""Repositories: thin abstractions over the ORM.

A repository is the only place that touches ``Model.objects`` for its
domain. Services orchestrate repositories. APIs orchestrate services.
This keeps queries reviewable and swappable (e.g. for caching layers).
"""
