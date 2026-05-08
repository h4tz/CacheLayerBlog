# Background Task Flow

## Explanation

Celery worker handles deferred work. The example here is order
settlement, but the pattern is general.

## Diagram

```mermaid
sequenceDiagram
    participant API
    participant Svc as OrderService
    participant Q as Redis Broker
    participant W as Celery Worker
    participant DB as Postgres

    API->>Svc: place_order
    Svc->>DB: INSERT order + items
    Svc-->>API: 201 order
    API-->>Q: dispatch settle_order
    Q-->>W: pick up task
    W->>DB: UPDATE order set status='paid'
    W-->>Q: ack
```

## Real-world reasoning

- The API stays sub-second by deferring slow side effects.
- Tasks are idempotent so a redelivery doesn't double-charge.

## Scaling considerations

- Worker concurrency is independent from web concurrency.
- Beat schedules periodic jobs (cleanups, aggregations).

## Possible bottlenecks

- Tasks blocking on external APIs without timeouts.

## Optimization ideas

- Per-task rate limits via Celery `rate_limit`.
- Dead-letter queue for repeated failures.
