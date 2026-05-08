# Phase 4 Learnings

## Production engineering

- **`tini` is non-negotiable.** Without a real PID 1, signal forwarding
  is unreliable.
- **Healthchecks belong in the container** so the orchestrator can act on
  them without external help.
- **JSON logs at every layer** (app + Nginx) collapse "what happened"
  investigations into a `jq` filter.

## Observability

- **Metrics first, traces later.** Prometheus + a single Grafana
  dashboard answers most production questions.
- **Dashboard as code.** Provisioning a dashboard from JSON beats
  hand-clicking it in a UI you can lose.

## Security

- **Defence in depth**: Nginx rate limit + DRF throttle + JWT rotation
  is cheap to keep.
- **Secrets discipline**: `.env` for the box, never the repo, never the
  CI logs.
- **Non-root containers** prevent escalation if any single layer is
  compromised.

## CI/CD

- **CI fails on lint** so style debates never block code review.
- **Deploy simulation** in CI catches Compose typos before the host
  does.
- **Tagged builds** (image SHA) make rollback a single command.

## Mistakes I avoided

- Running everything as root inside the container.
- A monolithic CI pipeline that only ran tests (skipping lint and image
  build).
- Caching everything forever and praying.
- "Deploy = SSH and pull". Replaced with `systemctl restart cachelayer`.

## Industry practices reinforced

- Multi-stage Docker for fast cold builds and small final images.
- Provisioned Grafana dashboards.
- VPS deploys via systemd-managed Compose units.
- Defence in depth at every layer.
