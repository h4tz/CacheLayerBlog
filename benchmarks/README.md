# Benchmarks

This directory holds *only* benchmark assets:

```
benchmarks/
  ab/                # ApacheBench shell scripts (quick smoke comparisons)
  locust/            # Locust user classes for sustained / burst tests
  pytest_benchmark/  # micro-benchmarks (validation, serialization, hot paths)
  reports/           # generated artifacts (CSV, HTML, charts) - gitignored
```

## Methodology (read this before publishing numbers)

1. **Same dataset.** Always reseed via `python manage.py seed_benchmark_data`
   with the same `--seed`. Two benchmarks on different data are not
   comparable.
2. **Same cache state.** Either always-cold (`redis-cli FLUSHDB`) or
   always-warm (one warmup pass per scenario). Mixing is a footgun.
3. **Same process model.** `gunicorn --workers N` for both rails. Same N.
4. **Same client.** Run Locust from the same machine, same Python.
5. **Disable rate-limit during benchmarking.** Set `BENCHMARK_MODE=true`.
   Re-enable afterwards.
6. **Report p95/p99, not just mean.** Mean hides tail latency.
7. **Capture environment.** App version, commit SHA, hardware, Python,
   Postgres, Redis versions — all in the report header.

## Quick start

```bash
# Bring up the stack
make up

# Seed deterministic data
docker compose -f infra/docker/docker-compose.yml exec app \
  python manage.py seed_benchmark_data --reset --users 1000 --products 5000

# ApacheBench smoke test (5k requests, 50 concurrency)
./benchmarks/ab/run_ab.sh

# Locust headless run (60s, 200 users, ramp 20/s)
./benchmarks/locust/run.sh

# pytest micro-benchmarks
pytest -m benchmark --benchmark-only --benchmark-save=phase3
```
