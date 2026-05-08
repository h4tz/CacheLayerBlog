# Phase 1 Learnings

## Architecture

- **Clean Architecture in a Django context** translates well: keep the ORM
  inside `repositories/` and you can change a query plan without touching a
  view.
- **Service layer pattern** is the difference between a 50-line view and a
  20-line view. The view focuses on transport. The service focuses on rules.
- **Modular monolith** beats early microservices: shipping fast and refactoring
  is cheaper than running a Kubernetes cluster for a side project.

## Production engineering

- **Settings package > settings file**: per-env deltas force you to think
  about which knob belongs where (security in `prod`, fixtures in `local`).
- **Structured logs** unlock greppable production output. JSON logs are
  cheap to add and free upside forever.
- **Request IDs everywhere**: the cheapest debugging tool ever invented.
- **Healthchecks belong in Docker** so orchestration can restart unhealthy
  containers without a human.

## API engineering

- **Stable error envelopes** are a contract. Clients can rely on
  `error.code` instead of regex-matching messages.
- **Versioned URLs** (`/api/v1/...`) keep your contract honest. Breaking
  changes go to `/api/v2/`, never silently into `/api/v1/`.
- **JWT** is a default, not a religion. SimpleJWT covers the 90% case.

## Performance engineering (foundation)

- **Don't optimize before measuring.** We added `prometheus-client` and
  request timing first; we'll know where to spend cycles in Phase 3.
- **`select_related` / `prefetch_related`** belong in repositories so views
  don't accidentally trigger N+1 by accident.

## Mistakes I avoided

- **Hardcoding `localhost`** anywhere. Use `DATABASE_URL` and `REDIS_URL`.
- **Mutating models in serializers.** Validation lives in serializers,
  *writes* live in services.
- **Mixing benchmark code with production code.** `BENCHMARK_MODE` is a
  feature flag with a single, narrow purpose.

## Industry practices reinforced

- Read-only base image with `tini` as PID 1.
- Multi-stage Docker build with wheels cached separately from runtime.
- CI fails on lint, not just tests.
