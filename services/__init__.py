"""Services: business logic and orchestration.

A service:
- accepts plain data (dataclasses, dicts) and returns plain data,
- never imports DRF or Ninja,
- is responsible for invariants, RBAC checks and transactional bounds.

Both rails (DRF + Ninja) call into the *exact same* service methods so the
benchmark isolates framework overhead and not business-logic differences.
"""
