# Repository Pattern Flow

## Explanation

The repository is the only layer that touches `Model.objects`. It owns
query plans (`select_related`, `prefetch_related`, indexes).

## Diagram

```mermaid
classDiagram
    class BaseRepository~T~ {
        +queryset() QuerySet
        +get(filters) T
        +exists(filters) bool
    }
    class UserRepository {
        +by_email(email) User
        +email_taken(email) bool
        +create_user(email,pw,role) User
        +list_active() QuerySet
    }
    class ProductRepository {
        +list_active(filters) QuerySet
        +get_by_sku(sku) Product
    }
    class CategoryRepository {
        +get_or_create_by_slug(name) Category
    }
    class OrderRepository {
        +for_user(user_id) QuerySet
        +create_with_items(user_id,note,items) Order
    }
    BaseRepository <|-- UserRepository
    BaseRepository <|-- ProductRepository
    BaseRepository <|-- CategoryRepository
    BaseRepository <|-- OrderRepository
```

## Real-world reasoning

- Centralising queries makes performance reviews tractable.
- Swapping the cache layer or moving to a read-replica is a one-file
  change inside the repository.

## Scaling considerations

- `select_related("category")` on `ProductRepository.queryset()`
  prevents N+1 in list views.

## Possible bottlenecks

- A repo method returning a raw `QuerySet` that's later filtered
  outside it (loses query plan ownership).

## Optimization ideas

- Add `count()` short-circuits using indexed columns only.
- Separate read and write repositories when the model warrants it.
