# Phase 3 Learnings

## Performance engineering

- **Measure tail latency, not mean.** Users see p99, not the average.
- **Cache state is part of the experiment.** Mixing warm and cold runs
  produces nonsense.
- **Profile before optimizing.** "It feels slow" is a hypothesis, not a
  diagnosis.
- **Bottleneck analysis**: most production "slowness" is N+1 queries or
  missing indexes — not framework choice.

## Benchmarking discipline

- Always pin: dataset seed, commit SHA, hardware, Python version, DB
  version.
- Always report: env, command, scenario, p50/p95/p99, error rate.
- Always run the exact same workload through both rails.

## Optimization wins typically come from

1. Indexing the field you actually filter on.
2. Eliminating N+1 with `select_related`/`prefetch_related`.
3. Caching read-mostly resources with explicit invalidation.
4. Moving heavy validation off the request path (queue + worker).

## When framework choice actually matters

- Tiny, validation-heavy endpoints called at extreme volume.
- Endpoints that serialize many small objects (e.g. lists of 100+).
- Anywhere ORM/IO time is *not* the dominant cost.

## Mistakes I avoided

- Reporting one number ("DRF is X% slower") without scenario context.
- Comparing rails with different middleware stacks.
- Forgetting to disable Django Debug Toolbar / DEBUG before measuring.

## Industry practices reinforced

- pytest-benchmark for micro, Locust for macro.
- `--benchmark-save` so trend analysis becomes possible.
- Reports are timestamped folders, never overwritten.
