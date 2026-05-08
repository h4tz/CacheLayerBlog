# Phase 3 — Benchmarking & Performance Engineering

## Goal

Quantify the DRF vs Ninja difference under realistic and stress conditions,
then drive an evidence-based optimization pass.

## Deliverables

- Locust suite covering both rails with identical workload mix.
- ApacheBench smoke scripts for fixed-size comparisons.
- pytest-benchmark micro-benchmarks isolating *validation* and
  *serialization* (the two layers that actually differ).
- `seed_benchmark_data` for reproducible datasets.
- Profiling scripts (`scripts/profile_endpoint.py`,
  `scripts/compare_rails.py`).
- Reproducible reports under `benchmarks/reports/<timestamp>/`.

## Methodology (the only thing that matters)

1. **Same dataset.** Always reseed via `seed_benchmark_data --seed 42`.
2. **Same cache state.** Either always-cold or always-warm.
3. **Same process model.** Same `gunicorn --workers N` value for both.
4. **Disable rate limiting.** `BENCHMARK_MODE=true`.
5. **Report tail latency.** Mean is misleading; report p50/p95/p99.
6. **Capture environment.** Commit SHA, hardware, Python, Postgres, Redis.

## Scenarios

| Scenario | Description | Why it matters |
|---|---|---|
| `health_only` | Only `/health` | Pure framework overhead, no DB. |
| `read_heavy` | 80% list/detail, 20% order placement | Realistic e-commerce mix. |
| `write_heavy` | 50/50 reads vs orders | Stresses transactional path. |
| `cold_cache` | `redis-cli FLUSHDB` between rounds | Worst case for read latency. |
| `warm_cache` | Single warmup pass | Best case; cache amortisation. |
| `validation_heavy` | 20-line order creation | Highlights validator cost. |

## Metrics to Capture

- **Latency**: p50, p95, p99 per rail per endpoint.
- **Throughput**: RPS at saturation.
- **Errors**: HTTP 5xx rate (must be 0 for a valid run).
- **CPU & RSS**: `docker stats` snapshot every 5s.
- **DB queries / request**: Prometheus or `connection.queries` capture.

## Step-by-Step

1. `make up && python manage.py seed_benchmark_data --reset`.
2. `BENCHMARK_MODE=true` and restart the app.
3. `./benchmarks/ab/run_ab.sh` — quick smoke.
4. `./benchmarks/locust/run.sh` — sustained run with HTML + CSV reports.
5. `pytest -m benchmark --benchmark-only --benchmark-save=phase3` — micro
   benchmarks for validation/serialization.
6. `python scripts/profile_endpoint.py /api/v1/drf/products/?page=1 200`
   — cProfile a hotspot.
7. Optimise (e.g. add `select_related`, swap `cache.delete` for prefix
   tag). Re-run. Save under a new report folder.

## Optimization Playbook

| Symptom | Likely cause | Fix |
|---|---|---|
| High DB queries / request | Missing `select_related`/`prefetch_related` | Move to repository layer. |
| List endpoint slow | No index on filter/order fields | Add `Index` in migration. |
| 99p tail spikes | GIL contention with sync workers | Increase workers; tune `WEB_CONCURRENCY`. |
| Validation dominates flame graph | Heavy DRF nested serializers | Switch hot paths to Ninja or use plain Python paths. |
| Latency rises with users | DB pool exhaustion | Tune `CONN_MAX_AGE` + Postgres `max_connections`. |

## Security Considerations

- Benchmark accounts use `@bench.example` so they cannot collide with real
  users.
- `BENCHMARK_MODE` is enforced off in `core.settings.prod`.

## Scaling Considerations

- A flat saturation curve means *the DB is the bottleneck*, not the framework.
  In that case the framework choice barely matters.
- A steep saturation curve means *the framework is the bottleneck*. That is
  where Ninja's lower per-request cost shines.

## Tradeoffs

- Locust scenarios are synthetic. Real users have think-time, retries and
  long-tail SKUs we are not simulating.
- Benchmark numbers are environment-relative. They are useful for *trend*
  detection across commits, less useful as absolute claims.

## Common Mistakes (avoided)

- Running with `DEBUG=True` (Django adds significant overhead).
- Comparing rails with rate-limit on for one and off for the other.
- Using mean as the primary metric.
- Not pinning the dataset, then "explaining" the differences.

## Real-world Engineering Notes

- The framework cost matters most for trivial endpoints (`/health`,
  `/me`). The deeper your business logic, the smaller the rail
  difference becomes.
- Ninja typically wins on validation-heavy endpoints because Pydantic v2
  (Rust-backed) is faster than DRF's pure-Python descriptor pipeline.
- DRF wins where you already lean on `ModelViewSet`, filter backends and
  permission classes.

## Interview Talking Points

- "How do you avoid drawing wrong conclusions from a benchmark?"
- "When does picking Ninja vs DRF actually move the dial in production?"
- "What does it mean when adding workers does not change throughput?"
