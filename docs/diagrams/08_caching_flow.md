# Caching Flow

## Explanation

Read cache for product detail with explicit invalidation.

## Diagram

```mermaid
flowchart LR
    Req[GET /products/SKU] --> Svc[ProductService.get]
    Svc -->|"HIT"| Resp[200 cached payload]
    Svc -->|"MISS"| Repo[ProductRepository.get_by_sku]
    Repo --> DB[(Postgres)]
    DB --> Repo
    Repo --> Svc
    Svc -->|"set 30s"| Cache[(Redis)]
    Svc --> Resp

    Write[PATCH /products/SKU/stock] --> Svc2[ProductService.update_stock]
    Svc2 --> DB
    Svc2 -->|"delete keys"| Cache
```

## Real-world reasoning

- Cache reads, never writes.
- Invalidate on the write path so stale values are bounded by the
  shorter of `TTL` and "next write".

## Scaling considerations

- Use cache prefix (`clb`) so shared Redis instances stay separable.
- Bounded TTL caps the worst-case staleness even if invalidation is
  missed.

## Possible bottlenecks

- Thundering herd on cache expiry. Add a small jitter to TTLs.

## Optimization ideas

- Tag-based invalidation (`cache.delete_many` by pattern) for bulk
  product imports.
