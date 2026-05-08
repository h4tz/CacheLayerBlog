# Phase 2 — Core APIs & Business Logic

## Goal

Ship equivalent business APIs on both rails (DRF and Ninja), backed by a
single set of services and repositories. Every business rule lives in
exactly one place.

## Deliverables

- JWT auth (SimpleJWT) reused by both rails so token formats match.
- RBAC with three roles (`admin`, `staff`, `customer`) enforced inside
  services, never inside views.
- `auth/register`, `auth/login`, `auth/me` on both rails.
- `products/` CRUD + filter + search + pagination on both rails.
- `orders/` placement with stock decrement + transactional invariants.
- Redis-backed read cache for product detail with explicit invalidation
  hooks in `ProductService`.
- Cross-rail parity tests so a payload-shape drift fails CI.
- `seed_benchmark_data` management command for reproducible loads.

## Architecture Decisions

| Decision | Reason |
|---|---|
| RBAC in services | Prevents transport-layer bypass; rules stay testable. |
| Same JWT validator on both rails | Eliminates the "auth differs" benchmark confound. |
| Decimal everywhere for money | Float arithmetic on currency is a bug factory. |
| Caches keyed by entity SKU | Cheap to invalidate; safe under concurrent updates. |
| Repository owns N+1 prevention | `select_related/prefetch_related` belong with queries, not views. |

## Endpoint Matrix

| Capability | DRF | Ninja |
|---|---|---|
| Health | `GET /api/v1/drf/health/` | `GET /api/v1/ninja/health` |
| Register | `POST /api/v1/drf/auth/register/` | `POST /api/v1/ninja/auth/register` |
| Login | `POST /api/v1/drf/auth/login/` | `POST /api/v1/ninja/auth/login` |
| Me | `GET /api/v1/drf/auth/me/` | `GET /api/v1/ninja/auth/me` |
| List products | `GET /api/v1/drf/products/` | `GET /api/v1/ninja/products/` |
| Create product (staff) | `POST /api/v1/drf/products/` | `POST /api/v1/ninja/products/` |
| Get product | `GET /api/v1/drf/products/{sku}/` | `GET /api/v1/ninja/products/{sku}` |
| Update stock (staff) | `PATCH /api/v1/drf/products/{sku}/stock/` | `PATCH /api/v1/ninja/products/{sku}/stock` |
| List orders | `GET /api/v1/drf/orders/` | `GET /api/v1/ninja/orders/` |
| Create order | `POST /api/v1/drf/orders/` | `POST /api/v1/ninja/orders/` |
| Get order | `GET /api/v1/drf/orders/{id}/` | `GET /api/v1/ninja/orders/{id}` |
| Update status (staff) | `PATCH /api/v1/drf/orders/{id}/status/` | `PATCH /api/v1/ninja/orders/{id}/status` |

## Step-by-Step

1. Implement `services.auth_service.AuthService` with register/login/issue.
2. Implement `services.product_service.ProductService` with cache + RBAC.
3. Implement `services.order_service.OrderService` with transaction.atomic
   bounds and stock invariants.
4. Wire DRF `views.py` + `serializers.py` to those services.
5. Wire Ninja routers (`auth_router`, `product_router`, `order_router`) to
   the same services using shared Pydantic schemas.
6. Centralise error envelope (`core.exceptions`) and register handlers in
   both rails.
7. Add factories + parity tests + RBAC tests.
8. Add `seed_benchmark_data` for reproducible Phase 3 datasets.

## Testing Strategy

- **Unit**: services and repositories under `tests/test_*.py` (no Client).
- **API**: DRF + Ninja tested via Django `Client` against real URLs.
- **Parity**: `tests/test_parity.py` runs identical inputs through both
  rails and asserts shape equivalence.
- **Authorization**: RBAC denial paths covered (customer can't
  `POST /products/`, customer can't read other users' orders).

## Benchmarking Strategy

- Cold cache vs warm cache: explicit `cache.clear()` between scenarios.
- Validation cost is benchmarked separately in Phase 3 with
  `pytest-benchmark` over the serializer / Pydantic boundary.

## Security Considerations

- Role escalation only happens via service methods that explicitly require
  staff via `_require_staff`.
- `min_length=8` on registration; full password validators run inside
  Django auth password validation chain in production.
- Orders cannot be read across users unless actor is staff.

## Scaling Considerations

- Index strategy: `(category, is_active)`, `(price)`, `(-created_at)` on
  products; `(user, -created_at)`, `(status, -created_at)` on orders.
- Read cache TTL is short (30s) to avoid staleness; invalidated explicitly
  on writes.

## Tradeoffs

- DRF + Ninja duplicate the routing layer. We accept this cost because
  removing it would invalidate the benchmark.
- We chose `SlugRelatedField`/string `category` instead of nested category
  objects to keep the JSON shape identical across rails.

## Common Mistakes (avoided)

- Putting `transaction.atomic` on the view instead of the service.
- Decrementing stock at the view layer (race condition).
- Returning DRF's default error format on Ninja and vice versa.

## Real-world Engineering Notes

- A "fair benchmark" is a discipline, not a button. Parity tests are how
  you keep it honest.
- Cache invalidation is hard but bounded: invalidate on the write path,
  TTL the read path.

## Interview Talking Points

- "How do you prevent business logic from leaking into transport?"
- "How does your RBAC survive a developer adding a new endpoint?"
- "What happens if two users place an order for the last unit?"
