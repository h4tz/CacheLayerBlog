"""Generic typed base repository.

We do not over-abstract here. The base only exists to centralise common
patterns (get-or-404, paginated list, exists). Domain-specific queries
should live on subclasses to keep query intent explicit.
"""

from __future__ import annotations

from typing import Generic, Iterable, TypeVar

from django.db.models import Model, QuerySet

from core.exceptions import NotFoundError

T = TypeVar("T", bound=Model)


class BaseRepository(Generic[T]):
    model: type[T]

    def queryset(self) -> QuerySet[T]:
        return self.model.objects.all()

    def get(self, **filters) -> T:
        try:
            return self.queryset().get(**filters)
        except self.model.DoesNotExist as exc:
            raise NotFoundError(
                f"{self.model.__name__} not found",
                {"filters": {k: str(v) for k, v in filters.items()}},
            ) from exc

    def exists(self, **filters) -> bool:
        return self.queryset().filter(**filters).exists()

    def all(self) -> Iterable[T]:
        return self.queryset()
