#!/usr/bin/env sh
set -eu

# Wait for the database to be reachable. We deliberately keep this script
# minimal: any networking complexity belongs in compose/k8s, not here.
if [ -n "${DATABASE_URL:-}" ]; then
    python - <<'PY'
import os, time, sys
from urllib.parse import urlparse
import socket

url = urlparse(os.environ["DATABASE_URL"])
host, port = url.hostname or "db", url.port or 5432
deadline = time.time() + 60
while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            sys.exit(0)
    except OSError:
        time.sleep(1)
print(f"Database {host}:{port} not reachable", file=sys.stderr)
sys.exit(1)
PY
fi

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    python manage.py migrate --noinput
fi

if [ "${COLLECT_STATIC:-false}" = "true" ]; then
    python manage.py collectstatic --noinput
fi

exec "$@"
