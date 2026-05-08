# Phase 1 — Foundation & Architecture

## Goal

Stand up a production-grade skeleton that lets us evolve the project into a
deployable, observable, benchmarkable backend. Both DRF and Ninja must mount
side-by-side over the *same* business logic.

## Deliverables (this phase)

- Modular monolith folder structure (`apps/`, `apis/`, `services/`,
  `repositories/`, `schemas/`, `core/`, `tests/`, `infra/`, `scripts/`,
  `benchmarks/`, `docs/`).
- Settings split into `core.settings.{base,local,test,prod}`.
- Custom `users.User` model with role enum (admin/staff/customer).
- Catalog (`Category`, `Product`) and Orders (`Order`, `OrderItem`) models +
  initial migrations.
- DRF rail at `/api/v1/drf/` and Ninja rail at `/api/v1/ninja/`, both with
  `health` endpoints.
- Structured JSON logging, request-id + timing middleware, standardised
  error envelopes shared across both rails.
- Dockerfile + Docker Compose stack (Postgres, Redis, app), `.env.example`.
- pytest config + smoke tests for both rails.
- GitHub Actions CI pipeline (lint + test + image build).
- Prometheus metrics endpoint (`/metrics`).

## Architecture Decisions

| Decision | Reason |
|---|---|
| Modular monolith | Fastest path to a fair DRF vs Ninja comparison; no service mesh complexity. |
| Settings inherit from `base` | Single source of truth; per-env modules only hold deltas. |
| `apps.*` for domain, `apis.*` for transport | Business logic is framework-agnostic and benchmarkable. |
| Shared services + repositories | Both rails call the same services so benchmark differences = framework cost. |
| Custom user from day one | Avoids painful migration later; lets us bind RBAC role to the user table. |
| `django-environ` for config | 12-factor compliance; same image runs in any env. |
| Prometheus + JSON logs from day one | Observability is an architectural decision, not an afterthought. |

## Folder Map (Phase 1 scope)

```
core/
  settings/{base,local,test,prod}.py
  middleware.py        # request-id + timing
  logging.py           # JSON formatter
  exceptions.py        # DomainError + envelope
  observability.py     # Prometheus helpers
apps/
  users/   models.py + admin.py + migrations
  catalog/ models.py + admin.py + migrations
  orders/  models.py + admin.py + migrations
apis/
  drf/v1/  serializers.py, views.py, urls.py
  ninja/v1/ api.py, auth.py, routers/*
services/    auth_service.py, product_service.py, order_service.py
repositories/ user_repository.py, product_repository.py, order_repository.py
schemas/     common.py, users.py, products.py, orders.py
infra/docker/  Dockerfile, docker-compose.yml
scripts/     entrypoint.sh
tests/       conftest.py, factories.py, test_health.py
.github/workflows/ci.yml
```

## Step-by-Step

1. Build settings split + env loading.
2. Add custom `users.User` and migrate.
3. Add `catalog` + `orders` models + migrations.
4. Add `services/` and `repositories/` boundaries.
5. Mount DRF v1 + Ninja v1 with health endpoints.
6. Wire RequestID + Timing middleware + JSON logging.
7. Add error envelope + DRF and Ninja exception handlers.
8. Containerise (Dockerfile + Compose).
9. Add CI pipeline.
10. Write smoke tests for both rails.

## Testing Strategy

- `tests/test_health.py` exercises both rails in isolation.
- Future API tests live next to their domain (e.g. `tests/test_orders_*.py`).
- pytest-django uses an in-memory SQLite DB by default for speed; integration
  tests can switch to Postgres via `DATABASE_URL` env override.

## Benchmarking Strategy (foundation only)

- Capture baseline `health` latency for each rail with `ApacheBench`:
  `ab -n 5000 -c 50 http://localhost:8000/api/v1/drf/health/`
  `ab -n 5000 -c 50 http://localhost:8000/api/v1/ninja/health`
- Store results in `benchmarks/reports/phase1/` for later regression comparison.

## Security Considerations

- No secrets in repo (`.env.example` only).
- JWT planned for Phase 2; throttling configured in DRF (off in benchmark mode).
- Production settings already harden HSTS, secure cookies, X-Frame-Options.

## Scaling Considerations

- Stateless app + Redis cache → horizontally scalable behind any LB.
- DB pooling and `CONN_MAX_AGE` exposed via env (defaults to 60s).

## Tradeoffs

- Two API rails increase code surface area. We accept that as the project's
  point: fairness > DRYness.
- Settings shim (`CacheLayerBlog/settings.py`) re-exports `core.settings.*` so
  legacy tooling keeps working; replace once all callers use `core.settings.*`.

## Common Mistakes (and what we did instead)

- *Putting business logic in serializers* → moved to `services/`.
- *Using default `auth.User`* → `users.User` from day one.
- *Single 800-line `settings.py`* → settings package with delta files.
- *Catching all exceptions in views* → centralised envelope in `core.exceptions`.

## Real-world Engineering Notes

- Adding observability *first* prevents "vibe-based" optimization later.
- Migrations from the default User to a custom one are painful; do it on day
  one or never.
- Environment-driven feature flags (`BENCHMARK_MODE`) let us run side-by-side
  experiments without forking branches.

## Interview Talking Points

- "How did you keep the DRF vs Ninja comparison fair?"
  Both rails call the *same* service methods; only transport changes.
- "How did you set up observability?"
  Request-id + structured JSON logs + Prometheus metrics from day one.
- "Why a modular monolith instead of microservices?"
  We are benchmarking framework cost, not network cost; the boundaries that
  matter are inside the process.
