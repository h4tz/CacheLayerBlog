# Database ER

## Explanation

Domain entities and relationships. Indexes are documented next to the
fields most queried.

## Diagram

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    CATEGORY ||--o{ PRODUCT : contains
    ORDER ||--|{ ORDER_ITEM : has
    PRODUCT ||--o{ ORDER_ITEM : referenced_by

    USER {
        bigint id PK
        string email UK
        string username UK
        string role "indexed"
        bool   is_active
    }
    CATEGORY {
        bigint id PK
        string name UK
        string slug UK
    }
    PRODUCT {
        bigint id PK
        string sku UK
        string name
        string slug UK
        decimal price "indexed"
        int stock
        bool is_active "composite idx (category, is_active)"
        datetime created_at "indexed desc"
    }
    ORDER {
        bigint id PK
        bigint user_id FK
        string status "composite idx (status, -created_at)"
        decimal total
        datetime created_at "composite idx (user, -created_at)"
    }
    ORDER_ITEM {
        bigint id PK
        bigint order_id FK
        bigint product_id FK
        int quantity
        decimal unit_price
        unique "(order_id, product_id)"
    }
```

## Real-world reasoning

- Composite indexes match the most common predicates
  (`WHERE user_id=? ORDER BY created_at DESC`).
- `(order, product)` is unique to prevent duplicate lines within a
  single order.

## Scaling considerations

- Hot path: orders listing for the current user. The composite index
  serves it without sorting.
- For very large catalogues, partition `Product` by `created_at` once
  >100M rows.

## Possible bottlenecks

- Aggregations (`SUM(total)`) over a long time window without
  pre-aggregation.

## Optimization ideas

- Materialised view for daily revenue.
- Move audit columns to a separate audit table when they dominate row
  size.
