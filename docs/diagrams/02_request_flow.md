# Request Flow

## Explanation

How a single API request flows through the system, regardless of rail.

## Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant N as Nginx
    participant W as Gunicorn
    participant M as Middleware
    participant API as DRF or Ninja
    participant S as Service
    participant R as Repository
    participant DB as Postgres

    C->>N: HTTPS request
    N->>W: HTTP + X-Request-ID
    W->>M: WSGI request
    M->>M: Assign request_id
    M->>API: Dispatch
    API->>S: Validated payload
    S->>R: Query / write
    R->>DB: SQL
    DB-->>R: rows
    R-->>S: domain objects
    S-->>API: result
    API-->>M: response
    M->>M: Record latency, set X-Response-Time-Ms
    M-->>W: response
    W-->>N: HTTP
    N-->>C: HTTPS response
```

## Real-world reasoning

- Putting the request id at the edge (Nginx) and propagating into the
  app gives you one correlation id end-to-end.
- The middleware-only timing means DRF and Ninja are measured by the
  exact same clock.

## Scaling considerations

- The path is shallow; per-request overhead is dominated by API +
  Service + DB.
- N+1 queries explode this picture by adding extra rows of `R-->DB`.

## Possible bottlenecks

- Service holding a transaction longer than necessary.
- Repository forgetting `select_related` causing N+1.

## Optimization ideas

- Capture `connection.queries` count per request and log when it exceeds
  a threshold.
