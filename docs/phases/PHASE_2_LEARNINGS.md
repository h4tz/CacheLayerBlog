# Phase 2 Learnings

## Architecture

- **One source of business truth** beats clever code. If two paths can both
  decrement stock, one of them is wrong.
- **DTOs at the edge, models in the middle.** Pydantic schemas (Ninja) and
  DRF serializers wrap the *same* model boundary; what's between them is
  framework-agnostic dataclasses.

## Performance

- **`select_related` and `prefetch_related` belong on the repository.**
  Pushing them to the view tempts other devs to forget them.
- **Short cache TTL + explicit invalidation** is usually right for
  read-mostly resources.
- **Pagination is mandatory** even on "small" lists. The day "small"
  becomes "huge" you'll already be in production.

## API engineering

- **Stable error codes** (`validation_error`, `conflict`, `not_found`)
  free clients from string parsing.
- **422 vs 400**: 422 for "well-formed but semantically invalid"; 400 for
  "I can't even parse this".
- **409 for stock conflicts** signals a retry-after-refetch contract.

## Production engineering

- **Service layer = the unit of replay.** Background workers should call
  the same service methods as the API.
- **Token rotation** (`ROTATE_REFRESH_TOKENS`) reduces blast radius if a
  refresh token leaks.

## Mistakes I avoided

- Using nested ORM objects in the response and breaking parity by accident.
- Inlining `Product.objects.get` in views.
- Letting caches outlive the actual invariants they encode.

## Industry practices reinforced

- Versioned URLs from day one.
- Centralised error envelopes.
- "If the test for parity fails, the benchmark is invalid" — drilled into
  CI.
