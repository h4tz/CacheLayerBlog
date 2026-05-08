"""Structured logging configuration.

We default to JSON logs in non-test environments so they are immediately
ingestible by Loki / CloudWatch / Stackdriver / Elastic without any
additional adapters. Switch to plain text in tests for readable output.
"""

from __future__ import annotations

import json
import logging
import logging.config
from typing import Any


class JsonFormatter(logging.Formatter):
    """Tiny dependency-free JSON log formatter.

    A bespoke formatter avoids dragging in ``python-json-logger`` and keeps
    the format under our explicit control (e.g. always emit request_id).
    """

    DEFAULT_FIELDS = (
        "name",
        "levelname",
        "msg",
        "module",
        "funcName",
        "lineno",
    )

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Pull through any structured extras (request_id, status, elapsed_ms...).
        for key, value in record.__dict__.items():
            if key in self.DEFAULT_FIELDS or key.startswith("_"):
                continue
            if key in ("args", "msg", "exc_info", "exc_text", "stack_info"):
                continue
            try:
                json.dumps(value)
            except TypeError:
                value = repr(value)
            payload[key] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO", json_logs: bool = True) -> None:
    """Apply our logging dictConfig.

    Called once during Django startup (see ``CacheLayerBlog/__init__.py``).
    """

    formatter = (
        {"()": "core.logging.JsonFormatter"}
        if json_logs
        else {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    )
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"default": formatter},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
            },
            "root": {"level": level, "handlers": ["console"]},
            "loggers": {
                "django.db.backends": {"level": "WARNING", "propagate": True},
                "clb": {"level": level, "propagate": True},
            },
        }
    )
