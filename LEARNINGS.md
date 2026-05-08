# Learnings (master file)

This file consolidates the most important takeaways across the four
phases. Each phase has its own deeper write-up under
[docs/phases/](docs/phases).

## Architecture & Clean Code

- **Clean architecture in Django** is achievable: keep the ORM in
  `repositories/`, the rules in `services/`, and the framework in
  `apis/`. Two rails (DRF + Ninja) prove the design holds.
- **Modular monolith first.** Network boundaries are expensive; pay for
  them only when the team / scale / fault-isolation justifies it.
- **The service layer is the unit of replay.** API, worker, scheduled
  job — they should all call the same method.

## API engineering

- **Versioned URLs from day one.** Breaking changes go to a new
  version, never silently into the old one.
- **Stable error envelopes.** Clients depend on `error.code`, never on
  string regexes.
- **Parity tests** are the only way to keep two API surfaces honest.

## Performance engineering

- **Measure tail latency** (p95/p99) — mean is misleading.
- **Profile before optimizing.** Replace "feels slow" with a flame
  graph.
- **Most "framework slowness" is N+1 queries.** Fix queries first;
  switch frameworks last.
- **Validation cost is real** for high-volume tiny endpoints. Pydantic
  v2 (Ninja) is faster on those; DRF wins ergonomically on heavily
  CRUD-shaped routes.

## Production engineering

- **Observability is an architectural decision.** Add Prometheus +
  structured logs *before* you need them.
- **Healthchecks belong in the container.** Orchestrators should not
  guess.
- **Defence in depth**: edge rate limit + app throttle + JWT rotation.
- **Boring deploys**: `systemctl restart cachelayer` is enough until
  scale demands more.

## Security

- **Custom user from day one.** Migrations later are painful.
- **RBAC inside services**, never inside views.
- **Non-root containers** with `tini` as PID 1.
- **Secrets via env**, never in the repo.

## Mistakes I avoided

- "DRF is slow" benchmarks that compared different endpoints.
- A monolithic `settings.py` that silently mixed local and prod.
- Mutating data in serializers / views.
- Catching all exceptions and returning `{"error": str(e)}`.

## Industry practices reinforced

- Multi-stage Docker.
- Provisioned dashboards.
- CI fails on lint *and* tests.
- Docs-as-code: every architecture diagram lives in `docs/diagrams/`
  and is reviewable in a PR.
