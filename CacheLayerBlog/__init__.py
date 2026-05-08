"""Project package.

Wires logging early so any import-time logs flow through the configured
JSON formatter.
"""

import os

from core.logging import configure_logging

configure_logging(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    json_logs=os.environ.get("LOG_JSON", "true").lower() == "true",
)
