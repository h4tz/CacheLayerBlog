# Benchmarking Pipeline

## Explanation

How we generate reproducible numbers comparing DRF vs Ninja.

## Diagram

```mermaid
flowchart LR
    Seed[seed_benchmark_data --seed 42] --> Pin[Pin commit SHA]
    Pin --> Mode[BENCHMARK_MODE=true]
    Mode --> Warm[Warmup pass]
    Warm --> AB[ApacheBench smoke]
    Warm --> Locust[Locust sustained]
    Warm --> PB[pytest-benchmark micro]
    AB --> Reports[(benchmarks/reports/<ts>)]
    Locust --> Reports
    PB --> Reports
    Reports --> Compare[Compare to previous run]
    Compare --> Doc[Phase doc / LEARNINGS]
```

## Real-world reasoning

- Each step is pinned (dataset, mode, warm state) so two runs are
  comparable.

## Scaling considerations

- Run the load generator from a separate machine to remove "client
  steals CPU" effects.

## Possible bottlenecks

- Locust running from the same VM as the app distorts results.

## Optimization ideas

- Trend dashboard from `--benchmark-save` JSON across commits.
