"""Domain apps package.

Each subpackage represents a bounded context. Apps must depend on
``services`` and ``repositories``, never on ``apis.*``. This keeps
business logic framework-agnostic and benchmarkable.
"""
