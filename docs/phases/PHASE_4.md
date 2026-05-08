# Phase 4 — Production Engineering & Proof of Work

## Goal

Make the system deployable, observable and secure on a single VPS so the
repository functions as a portfolio-quality showcase that a recruiter or
interviewer can stand up in minutes.

## Deliverables

- `docker-compose.prod.yml`: app + worker + beat + Postgres + Redis +
  Nginx + Prometheus + Grafana.
- Hardened `Dockerfile` (multi-stage, non-root user, `tini`, healthcheck).
- Nginx reverse proxy with edge rate limiting, JSON access logs, security
  headers and `/metrics` ACL.
- Celery worker + beat skeleton with a sample `settle_order` task.
- Prometheus scrape config + Grafana provisioning + sample dashboard
  comparing DRF and Ninja latency.
- systemd unit (`infra/systemd/cachelayer.service`) for the VPS.
- CI: lint + tests + image build (`.github/workflows/ci.yml`).
- CD simulation: image build + compose validation + `manage.py check`
  (`.github/workflows/deploy.yml`).

## Architecture Decisions

| Decision | Reason |
|---|---|
| Compose on a single VPS | Lowest barrier for portfolio reproducibility. |
| Nginx as edge | Free TLS, edge throttling, JSON access logs. |
| `tini` as PID 1 | Clean signal handling so SIGTERM => graceful drain. |
| Non-root container user | Limits blast radius of an RCE. |
| systemd-managed compose | OS-level supervision + automatic boot. |
| Prometheus first, traces later | Cheap to run; covers 80% of incidents. |

## Deploy Runbook (single VPS)

```bash
# 1. Provision a fresh Ubuntu 24.04 box and install Docker.
# 2. Clone the repo to /opt/cachelayer.
sudo mkdir -p /opt/cachelayer
sudo chown $USER /opt/cachelayer
git clone <repo> /opt/cachelayer
cd /opt/cachelayer

# 3. Create the production .env (copy .env.example, set strong secrets).
cp .env.example .env
$EDITOR .env

# 4. Install the systemd unit and enable on boot.
sudo cp infra/systemd/cachelayer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now cachelayer

# 5. Tail logs to verify.
docker compose -f infra/docker/docker-compose.prod.yml logs -f --tail=200

# 6. Verify health on the host.
curl -fsS http://127.0.0.1/api/v1/drf/health/
curl -fsS http://127.0.0.1/api/v1/ninja/health
```

## Security Checklist

- `DEBUG=False` in `core.settings.prod`.
- `SECURE_HSTS_*`, `SECURE_PROXY_SSL_HEADER`, secure cookies enabled.
- Container runs as the `app` user, not root.
- `.env` is on disk only; CI never sees real secrets.
- Nginx blocks `/metrics` from the public internet.
- DRF + edge rate limiting (defence in depth).
- JWT rotation on refresh.

## SLOs (initial)

| SLO | Target |
|---|---|
| Availability | 99.5% rolling 30d |
| API p95 latency (read) | < 250ms warm cache |
| API p99 latency (write) | < 1s |
| Error rate | < 0.5% 5xx |

## Scaling Strategy

- **Vertical first**: `WEB_CONCURRENCY` and Postgres tuning.
- **Horizontal**: replicate `app` container behind Nginx upstream.
- **Cache**: tune Redis maxmemory + LRU policy under load.
- **DB**: add read replicas; route read-only queries via a settings flag
  in the repository layer.
- **Workers**: scale Celery `--concurrency` first, then add worker
  replicas when CPU-bound.

## Tradeoffs

- Single VPS = single point of failure. Acceptable for portfolio /
  staging. Not for paid production.
- Compose lacks autoscaling. For real burst traffic, Kubernetes or a
  managed runtime is the right next step.

## Common Mistakes (avoided)

- Running gunicorn as root.
- Forgetting `proxy_set_header X-Forwarded-Proto`, breaking `is_secure`.
- Exposing `/metrics` publicly.
- Missing graceful drain on SIGTERM (we use `tini` + `--graceful-timeout`).

## Real-world Engineering Notes

- Operational readiness is its own deliverable. A healthy CI plus a
  visible dashboard is what makes a repo *credible* in an interview.
- A boring deploy is a good deploy. Compose + systemd + Nginx is enough
  to demonstrate the *concepts* without running a Kubernetes cluster.

## Interview Talking Points

- "How does graceful shutdown work in your container?"
- "Where does rate limiting live, and why both at Nginx and DRF?"
- "What happens to in-flight requests during a deploy?"
- "How would you turn this into a multi-node deployment?"
